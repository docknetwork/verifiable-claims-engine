import copy
import os
from typing import Generator, Dict, Tuple

from cert_core import Chain
from verifiable_claims.issuer.merkle_tree_generator import MerkleTreeGenerator
from cert_schema import normalize_jsonld
from eth_account.datastructures import AttributeDict
from web3 import Web3

from verifiable_claims.issuer.helpers import _get_random_from_csv


class SimplifiedCertificateBatchIssuer:
    """
    Class to issue blockcerts without relying on filesystem usage.

    Please note that it currently only supports anchoring to Ethereum.
    """

    def __init__(self, config: 'AttrDict', unsigned_certs: dict):
        # 1- Prepare config and unsigned certs (These come from my latest changes in cert-tools
        self.config = config
        self.config.original_chain = self.config.chain
        self.config.chain = Chain.parse_from_chain(self.config.chain)

        self.path_to_secret = os.path.join(config.usb_name, config.key_file)

        self.unsigned_certs = unsigned_certs
        self.cert_generator = self._create_cert_generator()

        # 2- Calculate Merkle Tree and Root
        self.merkle_tree_generator = MerkleTreeGenerator()
        self.merkle_tree_generator.populate(self.cert_generator)
        self.merkle_root = self.merkle_tree_generator.get_blockchain_data()

    def issue(self) -> Tuple[str, Dict]:
        """Anchor the merkle root in a blockchain transaction and add the tx id and merkle proof to each cert."""
        tx_id = self._broadcast_transaction()
        signed_certs = self._add_proof_to_certs(tx_id)
        return tx_id, signed_certs

    def _add_proof_to_certs(self, tx_id) -> Dict:
        """Add merkle proof to the JSON of the certificates."""
        proof_generator = self.merkle_tree_generator.get_proof_generator(tx_id, self.config.chain)
        signed_certs = copy.deepcopy(self.unsigned_certs)
        for _, cert in signed_certs.items():
            proof = next(proof_generator)
            cert['signature'] = proof
        return signed_certs

    def _broadcast_transaction(self) -> str:
        """Broadcast the tx used to anchor a merkle root to a given blockchain."""
        self.transaction_handler = SimplifiedEthereumTransactionHandler(
            chain=self.config.original_chain.split('_')[1],
            path_to_secret=self.path_to_secret,
            private_key=self.config.get('eth_private_key'),
            recommended_max_cost=self.config.gas_price * self.config.gas_limit,
            account_from=self.config.get('eth_public_key') or self.config.issuing_address,
        )
        tx_id = self.transaction_handler.issue_transaction(self.merkle_root)
        return tx_id

    def _create_cert_generator(self) -> Generator:
        """Return a generator of jsonld-normalized unsigned certs."""
        for uid, cert in self.unsigned_certs.items():
            normalized = normalize_jsonld(cert, detect_unmapped_fields=False)
            yield normalized.encode('utf-8')


class SimplifiedEthereumTransactionHandler:
    """Class to handle anchoring to the Ethereum network."""

    def __init__(
            self,
            chain: str,
            path_to_secret: str,
            private_key: str,
            recommended_max_cost: int,
            account_from: str,
            account_to: str = '0xdeaDDeADDEaDdeaDdEAddEADDEAdDeadDEADDEaD',
            max_retry=3

    ):
        self.max_retry = max_retry
        self.account_from = account_from
        self.account_to = account_to
        self.path_to_secret = path_to_secret

        self.eth_node_url = self._get_node_url(chain)

        self.web3 = Web3(Web3.HTTPProvider(self.eth_node_url))
        assert self.web3.isConnected()

        self._ensure_balance(recommended_max_cost)
        self.private_key = private_key or self._read_private_key()

    def issue_transaction(self, merkle_root: str, gas_price: int = 20000000000, gas_limit: int = 25000) -> str:
        """Broadcast a transaction with the merkle root as data and return the transaction id."""
        for i in range(self.max_retry):
            signed_tx = self._get_signed_tx(merkle_root, gas_price, gas_limit, i)
            try:
                tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                tx_id = self.web3.toHex(tx_hash)
                return tx_id
            except Exception as e:
                if i >= self.max_retry - 1:
                    raise
                continue

    def _get_signed_tx(self, merkle_root: str, gas_price: int, gas_limit: int, try_count: int) -> AttributeDict:
        """Prepare a raw transaction and sign it with the private key."""
        nonce = self.web3.eth.getTransactionCount(self.account_from)
        tx_info = {
            'nonce': nonce,
            'to': self.account_to,
            'value': 0,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'data': merkle_root,
        }
        if try_count:
            tx_info['nonce'] = tx_info['nonce'] + try_count
            tx_info['gas'] = self._factor_in_new_try(tx_info['gas'], try_count)
            tx_info['gasPrice'] = self._factor_in_new_try(tx_info['gasPrice'], try_count)
        signed_tx = self.web3.eth.account.sign_transaction(tx_info, self.private_key)
        return signed_tx

    @staticmethod
    def _factor_in_new_try(number, try_count) -> int:
        """Increase the given number with 10% with each try."""
        factor = float(f"1.{try_count}")
        return int(number * factor)

    def _read_private_key(self) -> str:
        """Read private key from file."""
        with open(self.path_to_secret) as key_file:
            key = key_file.read().strip()
        return key

    def _ensure_balance(self, recommended_max_cost) -> None:
        """Make sure that the Ethereum account's balance is enough to cover the tx costs."""
        assert self.web3.eth.getBalance(self.account_from) >= recommended_max_cost

    @staticmethod
    def _get_node_url(chain: str) -> str:
        """Returns the url to a node for the chosen chain. It is possible to provide multiple values in the envvar."""
        if chain == 'mainnet':
            return _get_random_from_csv(os.environ.get('ETH_NODE_URL_MAINNET'))
        elif chain == 'ropsten':
            return _get_random_from_csv(os.environ.get('ETH_NODE_URL_ROPSTEN'))

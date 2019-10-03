# Blockcerts issuing module

Allows the node to issue Blockcerts.

We have stopped tracking the original `cert-tools` and `cert-issuer` repos from MIT since they were outdated. 
We're using our version of them which allow in-memory issuing, have no race conditions and are simpler to use as Python modules. 

## TODO:
- [x] Wrapper around blockcerts-issuing code
- [x] Use in-memory issuing (as opposed to the filesystem-intensive issuing flow implemented by MIT)
    - [x] Remove old logic
    - [x] Remove unused dirs
- [ ] Clean constants and implement config file instead
- [x] Simplify `issuer` code
- [ ] Unify `tools` and `issuer` modules
- [ ] Proper payload validation
    - [ ] Useful error messages
- [x] Recipient-specific HTML compilation from template + tags. 
- [ ] Better keys for recipient payloads (e.g. 'identity vs email')
- [ ] Robust datetime parsing for expiration (so the caller doesn't need to know the exact format)
- [ ] Return baked images?
  - [ ] Gzipped?
- [ ] Final Blockcerts validation before returning

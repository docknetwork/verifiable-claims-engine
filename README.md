# Verifiable Claims Engine

Python reference implementation of a verifiable claims issuing engine.


## Module-specific Readmes

- [Blockcerts issuing](blockcerts/README.md)
- [Cost](cost/README.md)
- [Bidding](bidding/README.md)

## Development info

### Build image
```bash
docker build -t verifiable-claims-engine --build-arg DEV=1 .
```

### Bash inside container
```bash
docker run -it --rm --name verifiable-claims-engine  --mount type=bind,source=$(pwd),target=/app verifiable-claims-engine bash
```

### Access http locally
```bash
docker run -it --rm --name verifiable-claims-engine --mount type=bind,source=$(pwd),target=/app -p 8080:80 verifiable-claims-engine
```
then visit `127.0.0.1:8080` in your web browser or run `curl 127.0.0.1:8080/ping`
to verify it's running.

### Run tests
```bash
docker run -it --rm --name verifiable-claims-engine  --mount type=bind,source=$(pwd),target=/app verifiable-claims-engine pytest tests
```

#### Create app in python cli
```python
import os
from flaskapp.app import create_app
app = create_app(config_data=os.environ)
```

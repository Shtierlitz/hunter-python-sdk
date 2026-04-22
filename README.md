# Hunter Python SDK

Small synchronous Python SDK for the Hunter.io API v2.

The package exposes:

- `HunterClient` for direct API calls
- `HunterService` for API calls plus persistence
- `InMemoryStorage` as a simple dictionary-backed CRUD storage

Implemented endpoints:

- Domain Search
- Email Finder
- Email Verifier

## Requirements

- Python 3.11+
- Poetry

## Installation

Install the package:

```bash
poetry install
```

Install the package with development tooling:

```bash
poetry install --extras dev
```

## Usage

### Direct client usage

```python
from hunter_sdk.client import HunterClient

client = HunterClient(api_key='test-api-key')

domain_result = client.domain_search(domain='example.com')
print(domain_result.domain)
print(domain_result.email_count)

finder_result = client.email_finder(
    domain='example.com',
    first_name='Jane',
    last_name='Doe',
)
print(finder_result.email)

verification_result = client.email_verifier(email='jane@example.com')
print(verification_result.status)
print(verification_result.is_pending)
```

### Service usage with storage

```python
from hunter_sdk.client import HunterClient
from hunter_sdk.service import HunterService
from hunter_sdk.storage import InMemoryStorage

storage = InMemoryStorage()
client = HunterClient(api_key='test-api-key')
service = HunterService(client=client, storage=storage)

domain_record = service.search_domain(domain='example.com')
finder_record = service.find_email(
    domain='example.com',
    first_name='Jane',
    last_name='Doe',
)
verifier_record = service.verify_email(email='jane@example.com')

print(domain_record.id)
print(finder_record.operation_result)
print(verifier_record.operation_result)
print(storage.list())
```

### CRUD storage example

```python
from hunter_sdk.storage import InMemoryStorage

storage = InMemoryStorage()
records = storage.list()
print(records)
```

## Error handling

The client raises:

- `HunterApiError` when Hunter returns a non-success HTTP response
- `HunterTransportError` when the HTTP request itself fails

Example:

```python
from hunter_sdk.client import HunterClient
from hunter_sdk.exceptions import HunterApiError, HunterTransportError

client = HunterClient(api_key='test-api-key')

try:
    result = client.domain_search(domain='example.com')
    print(result)
except HunterApiError as api_error:
    print(api_error.status_code)
    print(api_error.errors)
except HunterTransportError as transport_error:
    print(transport_error)
```

## Development

Run tests:

```bash
poetry run pytest
```

Run type checking:

```bash
poetry run mypy src tests
```

Run linting:

```bash
poetry run flake8 src tests
```

Optional smoke demo:

```bash
poetry run python examples/smoke_demo.py
```

`examples/smoke_demo.py` is an optional runnable example for manual smoke testing.
It is included to demonstrate the SDK against the supported Hunter endpoints and is not part of the required implementation.


Override demo inputs by creating a local `.env` file in the project root:

```dotenv
HUNTER_API_KEY=test-api-key
HUNTER_DOMAIN=stripe.com
HUNTER_FIRST_NAME=Patrick
HUNTER_LAST_NAME=Collison
HUNTER_EMAIL=patrick@stripe.com
```

Then run:

```bash
poetry run python examples/smoke_demo.py
```

## Notes

- The SDK is intentionally synchronous and small.
- Persistence is in-memory only.
- `test-api-key` is suitable for smoke-level examples and local verification of supported endpoints.

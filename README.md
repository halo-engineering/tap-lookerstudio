# tap-lookerstudio

Singer tap for Google Looker Studio (formerly Data Studio) asset metadata, built on the [Meltano Singer SDK](https://sdk.meltano.com/) (`v0.42`).

Intended for the HALO Connect data pipeline (built on Hotglue). No existing Singer tap covers the Looker Studio API — all existing `tap-looker` implementations target the separate Looker enterprise product.

## Streams

The Looker Studio API is limited to asset metadata and permissions. This tap covers the full API surface:

| Stream | Replication | Key(s) | Description |
|---|---|---|---|
| `reports` | INCREMENTAL (`updateTime`) | `name` | Report assets |
| `data_sources` | INCREMENTAL (`updateTime`) | `name` | Data source assets |
| `report_permissions` | FULL_TABLE | `asset_name`, `role`, `member` | Permissions per report (child of `reports`) |
| `data_source_permissions` | FULL_TABLE | `asset_name`, `role`, `member` | Permissions per data source (child of `data_sources`) |

Permissions are flattened from `{role: {members: [...]}}` into `(asset_name, role, member)` rows for direct SQL querying.

## Prerequisites

- Python >= 3.9
- A Google Cloud service account with [domain-wide delegation](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) enabled
- The scope `https://www.googleapis.com/auth/datastudio.readonly` authorized in Google Admin console
- A Google Workspace user email to impersonate

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Copy the example config and fill in your credentials:

```bash
cp config.json.example config.json
```

| Setting | Type | Required | Default | Description |
|---|---|---|---|---|
| `service_account_json` | object | Yes | — | Full Google service account key JSON (parsed object, not a file path) |
| `delegated_user_email` | string | Yes | — | Workspace user email to impersonate via domain-wide delegation |
| `include_trashed` | boolean | No | `false` | Include trashed assets |
| `owner_filter` | string | No | — | Filter assets by owner email |
| `start_date` | datetime | No | — | Initial bookmark for incremental streams |

## Usage

```bash
# Validate credentials and discover available streams
tap-lookerstudio --discover --config config.json

# Run extraction (outputs Singer messages to stdout)
tap-lookerstudio --config config.json

# Save output for inspection
tap-lookerstudio --config config.json > output.jsonl

# Pipe to a target (e.g. target-jsonl, target-postgres)
tap-lookerstudio --config config.json | target-jsonl
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests (20 tests, all mocked — no credentials needed)
pytest

# Lint
ruff check .
```

## Project Structure

```
tap_lookerstudio/
├── tap.py       # TapLookerStudio entry point and config schema
├── client.py    # LookerStudioStream base (RESTStream) with error handling
├── auth.py      # Google service account authenticator with domain-wide delegation
└── streams.py   # ReportsStream, DataSourcesStream, and permissions child streams
tests/
├── conftest.py      # Shared fixtures and sample API responses
├── test_core.py     # Discovery, schema, config validation
├── test_streams.py  # Mocked HTTP: pagination, flattening, 404/403 handling
└── test_auth.py     # Credential creation, refresh, caching
```

## References

- [Looker Studio API](https://developers.google.com/looker-studio/integrate/api)
- [Meltano Singer SDK](https://sdk.meltano.com/)
- Previous integration (targets different Looker product): [hotglue/tap-looker](https://gitlab.com/hotglue/tap-looker)

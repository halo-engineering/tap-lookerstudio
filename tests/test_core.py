"""SDK-level tests for tap-lookerstudio (discovery, config, schema validation)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tap_lookerstudio.tap import TapLookerStudio

_SAMPLE_CONFIG = {
    "service_account_json": {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nfake\n-----END RSA PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    },
    "delegated_user_email": "admin@example.com",
}


class TestTapDiscovery:
    """Test tap discovery and catalog generation without real API calls."""

    def test_discover_streams(self):
        tap = TapLookerStudio(config=_SAMPLE_CONFIG)
        streams = tap.discover_streams()
        stream_names = {s.name for s in streams}
        assert stream_names == {
            "reports",
            "data_sources",
            "report_permissions",
            "data_source_permissions",
        }

    def test_catalog_has_all_streams(self):
        tap = TapLookerStudio(config=_SAMPLE_CONFIG)
        catalog = tap.catalog_dict
        stream_names = {entry["stream"] for entry in catalog["streams"]}
        assert "reports" in stream_names
        assert "data_sources" in stream_names
        assert "report_permissions" in stream_names
        assert "data_source_permissions" in stream_names

    def test_reports_schema_has_description(self):
        tap = TapLookerStudio(config=_SAMPLE_CONFIG)
        reports = tap.streams["reports"]
        props = reports.schema["properties"]
        assert "description" in props
        assert "name" in props
        assert "updateTime" in props

    def test_data_sources_schema_lacks_description(self):
        tap = TapLookerStudio(config=_SAMPLE_CONFIG)
        ds = tap.streams["data_sources"]
        props = ds.schema["properties"]
        assert "description" not in props
        assert "name" in props

    def test_reports_incremental(self):
        tap = TapLookerStudio(config=_SAMPLE_CONFIG)
        reports = tap.streams["reports"]
        assert reports.replication_key == "updateTime"
        assert reports.is_sorted is False

    def test_permissions_full_table(self):
        tap = TapLookerStudio(config=_SAMPLE_CONFIG)
        perms = tap.streams["report_permissions"]
        assert perms.replication_key is None

    def test_config_validation_missing_required(self):
        with pytest.raises(Exception):
            TapLookerStudio(config={"service_account_json": {}})

    def test_cli_prints_version(self, capsys):
        """Verify CLI --version works."""
        with pytest.raises(SystemExit):
            TapLookerStudio.cli(args=["--version"])

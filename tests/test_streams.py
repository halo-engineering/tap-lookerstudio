"""Unit tests for stream logic with mocked HTTP responses."""

from __future__ import annotations

from unittest.mock import patch

import responses

from tests.conftest import (
    SAMPLE_DATA_SOURCES_RESPONSE,
    SAMPLE_PERMISSIONS_RESPONSE,
    SAMPLE_REPORTS_PAGE1,
    SAMPLE_REPORTS_PAGE2,
    SAMPLE_REPORTS_RESPONSE,
)
from tap_lookerstudio.tap import TapLookerStudio

API_BASE = "https://datastudio.googleapis.com/v1"


def _noop_authenticate(self, request):
    request.headers["Authorization"] = "Bearer fake"
    return request


def _patch_auth():
    """Return a patch that bypasses Google auth."""
    return patch(
        "tap_lookerstudio.auth.GoogleServiceAccountAuthenticator.authenticate_request",
        _noop_authenticate,
    )


def _make_tap(config):
    """Create a tap instance with auth patched out."""
    return TapLookerStudio(config=config)


class TestReportsStream:
    @responses.activate
    def test_fetches_reports(self, sample_config):
        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json=SAMPLE_REPORTS_RESPONSE,
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["reports"]
            records = list(stream.get_records(context=None))

        assert len(records) == 1
        assert records[0]["name"] == "assets/report1"
        assert records[0]["title"] == "Test Report"
        assert records[0]["assetType"] == "REPORT"

    @responses.activate
    def test_pagination(self, sample_config):
        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json=SAMPLE_REPORTS_PAGE1,
            status=200,
        )
        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json=SAMPLE_REPORTS_PAGE2,
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["reports"]
            records = list(stream.get_records(context=None))

        assert len(records) == 2
        assert records[0]["name"] == "assets/report1"
        assert records[1]["name"] == "assets/report2"

    @responses.activate
    def test_query_params_include_trashed(self, sample_config):
        sample_config["include_trashed"] = True
        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json=SAMPLE_REPORTS_RESPONSE,
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["reports"]
            list(stream.get_records(context=None))

        assert "includeTrashed=true" in responses.calls[0].request.url

    @responses.activate
    def test_query_params_owner_filter(self, sample_config):
        sample_config["owner_filter"] = "owner@example.com"
        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json=SAMPLE_REPORTS_RESPONSE,
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["reports"]
            list(stream.get_records(context=None))

        assert "owner=owner" in responses.calls[0].request.url


class TestDataSourcesStream:
    @responses.activate
    def test_fetches_data_sources(self, sample_config):
        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json=SAMPLE_DATA_SOURCES_RESPONSE,
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["data_sources"]
            records = list(stream.get_records(context=None))

        assert len(records) == 1
        assert records[0]["name"] == "assets/ds1"
        assert records[0]["assetType"] == "DATA_SOURCE"


class TestPermissionsFlattening:
    @responses.activate
    def test_flattens_permissions(self, sample_config):
        responses.add(
            responses.GET,
            f"{API_BASE}/assets/assets/report1/permissions",
            json=SAMPLE_PERMISSIONS_RESPONSE,
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["report_permissions"]
            context = {"asset_name": "assets/report1", "asset_type": "REPORT"}
            records = list(stream.get_records(context=context))

        assert len(records) == 4
        roles = {r["role"] for r in records}
        assert roles == {"OWNER", "EDITOR", "VIEWER"}

        owner_records = [r for r in records if r["role"] == "OWNER"]
        assert len(owner_records) == 1
        assert owner_records[0]["member"] == "user:owner@example.com"
        assert owner_records[0]["asset_name"] == "assets/report1"
        assert owner_records[0]["asset_type"] == "REPORT"

        editor_records = [r for r in records if r["role"] == "EDITOR"]
        assert len(editor_records) == 2

    @responses.activate
    def test_empty_permissions(self, sample_config):
        responses.add(
            responses.GET,
            f"{API_BASE}/assets/assets/report1/permissions",
            json={"permissions": {}},
            status=200,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["report_permissions"]
            context = {"asset_name": "assets/report1", "asset_type": "REPORT"}
            records = list(stream.get_records(context=context))

        assert len(records) == 0

    @responses.activate
    def test_404_skips_deleted_asset(self, sample_config):
        responses.add(
            responses.GET,
            f"{API_BASE}/assets/assets/deleted1/permissions",
            json={"error": {"code": 404, "message": "Not found"}},
            status=404,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["report_permissions"]
            context = {"asset_name": "assets/deleted1", "asset_type": "REPORT"}
            records = list(stream.get_records(context=context))

        # Should not raise, should return empty
        assert len(records) == 0


class TestErrorHandling:
    @responses.activate
    def test_403_raises_fatal_error(self, sample_config):
        from singer_sdk.exceptions import FatalAPIError

        responses.add(
            responses.GET,
            f"{API_BASE}/assets:search",
            json={"error": {"code": 403, "message": "Forbidden"}},
            status=403,
        )

        with _patch_auth():
            tap = _make_tap(sample_config)
            stream = tap.streams["reports"]
            try:
                list(stream.get_records(context=None))
                assert False, "Should have raised FatalAPIError"
            except FatalAPIError as e:
                assert "Access denied" in str(e)
                assert "domain-wide delegation" in str(e)

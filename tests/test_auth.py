"""Unit tests for Google service account authentication."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests


class TestGoogleServiceAccountAuthenticator:
    def test_creates_credentials_with_subject(self, sample_config):
        """Verify with_subject is called with delegated_user_email."""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_delegated_creds = MagicMock()
        mock_delegated_creds.valid = True
        mock_delegated_creds.token = "test-token-123"
        mock_creds.with_subject.return_value = mock_delegated_creds

        with (
            patch(
                "tap_lookerstudio.auth.service_account.Credentials.from_service_account_info",
                return_value=mock_creds,
            ) as mock_from_sa,
            patch("tap_lookerstudio.auth.Request"),
        ):
            from tap_lookerstudio.auth import GoogleServiceAccountAuthenticator

            mock_stream = MagicMock()
            mock_stream.config = sample_config
            mock_stream.tap_name = "tap-lookerstudio"
            mock_stream.logger = MagicMock()
            auth = GoogleServiceAccountAuthenticator(stream=mock_stream)

            req = requests.PreparedRequest()
            req.headers = {}
            auth.authenticate_request(req)

            mock_from_sa.assert_called_once()
            mock_creds.with_subject.assert_called_once_with("admin@example.com")
            assert req.headers["Authorization"] == "Bearer test-token-123"

    def test_refreshes_expired_credentials(self, sample_config):
        """Verify credentials are refreshed when expired."""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_delegated_creds = MagicMock()
        mock_delegated_creds.valid = False  # Expired
        mock_delegated_creds.token = "refreshed-token"
        mock_creds.with_subject.return_value = mock_delegated_creds

        mock_request = MagicMock()

        with (
            patch(
                "tap_lookerstudio.auth.service_account.Credentials.from_service_account_info",
                return_value=mock_creds,
            ),
            patch("tap_lookerstudio.auth.Request", return_value=mock_request),
        ):
            from tap_lookerstudio.auth import GoogleServiceAccountAuthenticator

            mock_stream = MagicMock()
            mock_stream.config = sample_config
            mock_stream.tap_name = "tap-lookerstudio"
            mock_stream.logger = MagicMock()
            auth = GoogleServiceAccountAuthenticator(stream=mock_stream)

            req = requests.PreparedRequest()
            req.headers = {}
            auth.authenticate_request(req)

            mock_delegated_creds.refresh.assert_called_once_with(mock_request)
            assert req.headers["Authorization"] == "Bearer refreshed-token"

    def test_lazy_creation_caches_credentials(self, sample_config):
        """Verify credentials are created once and reused."""
        mock_creds = MagicMock()
        mock_delegated_creds = MagicMock()
        mock_delegated_creds.valid = True
        mock_delegated_creds.token = "cached-token"
        mock_creds.with_subject.return_value = mock_delegated_creds

        with (
            patch(
                "tap_lookerstudio.auth.service_account.Credentials.from_service_account_info",
                return_value=mock_creds,
            ) as mock_from_sa,
            patch("tap_lookerstudio.auth.Request"),
        ):
            from tap_lookerstudio.auth import GoogleServiceAccountAuthenticator

            mock_stream = MagicMock()
            mock_stream.config = sample_config
            mock_stream.tap_name = "tap-lookerstudio"
            mock_stream.logger = MagicMock()
            auth = GoogleServiceAccountAuthenticator(stream=mock_stream)

            # Authenticate twice
            for _ in range(2):
                req = requests.PreparedRequest()
                req.headers = {}
                auth.authenticate_request(req)

            # from_service_account_info should only be called once
            mock_from_sa.assert_called_once()

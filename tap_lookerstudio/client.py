"""Base REST stream client for Looker Studio API."""

from __future__ import annotations

import logging
from functools import cached_property

from singer_sdk.exceptions import FatalAPIError
from singer_sdk.streams import RESTStream

from tap_lookerstudio.auth import GoogleServiceAccountAuthenticator

logger = logging.getLogger(__name__)


class LookerStudioStream(RESTStream):
    """Base stream class for Looker Studio API endpoints."""

    url_base = "https://datastudio.googleapis.com/v1"
    records_jsonpath = "$.assets[*]"

    @cached_property
    def authenticator(self) -> GoogleServiceAccountAuthenticator:
        """Return a cached authenticator for this stream."""
        return GoogleServiceAccountAuthenticator(stream=self)

    def validate_response(self, response) -> None:
        """Handle Looker Studio specific error responses."""
        if response.status_code == 403:
            msg = (
                f"Access denied to Looker Studio API (HTTP 403). "
                f"Verify the service account has domain-wide delegation enabled "
                f"and the correct scopes are authorized. Response: {response.text}"
            )
            raise FatalAPIError(msg)
        if response.status_code == 404 and hasattr(self, "parent_stream_type"):
            logger.warning(
                "Asset not found (HTTP 404) for %s — may have been deleted. Skipping.",
                self.name,
            )
            return
        super().validate_response(response)

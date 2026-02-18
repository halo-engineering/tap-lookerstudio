"""Google Service Account authenticator for Looker Studio API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests as requests_lib
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from singer_sdk.authenticators import APIAuthenticatorBase

if TYPE_CHECKING:
    from singer_sdk.streams import RESTStream

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/datastudio.readonly"]


class GoogleServiceAccountAuthenticator(APIAuthenticatorBase):
    """Authenticator using Google service account with domain-wide delegation."""

    def __init__(self, stream: RESTStream) -> None:
        super().__init__(stream=stream)
        self._credentials: service_account.Credentials | None = None

    @property
    def credentials(self) -> service_account.Credentials:
        """Lazily create and return credentials, refreshing if expired."""
        if self._credentials is None:
            sa_json = self.config["service_account_json"]
            creds = service_account.Credentials.from_service_account_info(
                sa_json,
                scopes=SCOPES,
            )
            delegated_email = self.config["delegated_user_email"]
            self._credentials = creds.with_subject(delegated_email)
            logger.info("Created credentials delegated to %s", delegated_email)

        if not self._credentials.valid:
            self._credentials.refresh(Request())

        return self._credentials

    def authenticate_request(
        self, request: requests_lib.PreparedRequest
    ) -> requests_lib.PreparedRequest:
        """Add Bearer token to the request."""
        request.headers["Authorization"] = f"Bearer {self.credentials.token}"
        return request

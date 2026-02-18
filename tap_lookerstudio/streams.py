"""Stream classes for Looker Studio API."""

from __future__ import annotations

from typing import Any, Iterable

from singer_sdk import typing as th
from singer_sdk.pagination import JSONPathPaginator

from tap_lookerstudio.client import LookerStudioStream

_COMMON_ASSET_PROPS = [
    th.Property("name", th.StringType, required=True, description="Asset resource name"),
    th.Property("assetType", th.StringType, description="REPORT or DATA_SOURCE"),
    th.Property("title", th.StringType, description="Display title"),
    th.Property("owner", th.StringType, description="Owner email"),
    th.Property("creator", th.StringType, description="Creator email"),
    th.Property("createTime", th.DateTimeType, description="Creation timestamp"),
    th.Property("updateTime", th.DateTimeType, description="Last update timestamp"),
    th.Property(
        "updateByMeTime", th.DateTimeType, description="Last update by delegated user"
    ),
    th.Property(
        "lastViewByMeTime", th.DateTimeType, description="Last view by delegated user"
    ),
    th.Property("trashed", th.BooleanType, description="Whether asset is trashed"),
]

_REPORT_PROPERTIES = th.PropertiesList(
    *_COMMON_ASSET_PROPS,
    th.Property("description", th.StringType, description="Report description"),
)

_DATA_SOURCE_PROPERTIES = th.PropertiesList(*_COMMON_ASSET_PROPS)

_PERMISSION_PROPERTIES = th.PropertiesList(
    th.Property("asset_name", th.StringType, required=True, description="Parent asset name"),
    th.Property("role", th.StringType, required=True, description="Permission role"),
    th.Property("member", th.StringType, required=True, description="Member identifier"),
    th.Property("asset_type", th.StringType, description="REPORT or DATA_SOURCE"),
)


class ReportsStream(LookerStudioStream):
    """Stream for Looker Studio report assets."""

    name = "reports"
    path = "/assets:search"
    primary_keys = ("name",)
    replication_key = "updateTime"
    is_sorted = False
    schema = _REPORT_PROPERTIES.to_dict()

    def get_new_paginator(self) -> JSONPathPaginator:
        return JSONPathPaginator("$.nextPageToken")

    def get_url_params(
        self, context: dict | None, next_page_token: str | None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"assetTypes": "REPORT"}
        if next_page_token:
            params["pageToken"] = next_page_token
        if self.config.get("include_trashed"):
            params["includeTrashed"] = "true"
        if self.config.get("owner_filter"):
            params["owner"] = self.config["owner_filter"]
        return params

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        return {"asset_name": record["name"], "asset_type": "REPORT"}


class DataSourcesStream(LookerStudioStream):
    """Stream for Looker Studio data source assets."""

    name = "data_sources"
    path = "/assets:search"
    primary_keys = ("name",)
    replication_key = "updateTime"
    is_sorted = False
    schema = _DATA_SOURCE_PROPERTIES.to_dict()

    def get_new_paginator(self) -> JSONPathPaginator:
        return JSONPathPaginator("$.nextPageToken")

    def get_url_params(
        self, context: dict | None, next_page_token: str | None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"assetTypes": "DATA_SOURCE"}
        if next_page_token:
            params["pageToken"] = next_page_token
        if self.config.get("include_trashed"):
            params["includeTrashed"] = "true"
        if self.config.get("owner_filter"):
            params["owner"] = self.config["owner_filter"]
        return params

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        return {"asset_name": record["name"], "asset_type": "DATA_SOURCE"}


class _PermissionsStream(LookerStudioStream):
    """Base class for permissions child streams."""

    records_jsonpath = "$"  # We parse the response manually in parse_response
    primary_keys = ("asset_name", "role", "member")
    replication_key = None
    ignore_parent_replication_keys = True

    schema = _PERMISSION_PROPERTIES.to_dict()

    def get_url(self, context: dict | None) -> str:
        """Build URL without encoding slashes in asset_name."""
        asset_name = (context or {}).get("asset_name", "")
        return f"{self.url_base}/assets/{asset_name}/permissions"

    def get_url_params(
        self, context: dict | None, next_page_token: str | None
    ) -> dict[str, Any]:
        return {}

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Override to store context for use in parse_response."""
        self._current_context = context
        yield from super().get_records(context)

    def parse_response(self, response) -> Iterable[dict]:
        """Flatten permissions from {role: {members: [...]}} into rows."""
        data = response.json()
        permissions = data.get("permissions", {})
        context = getattr(self, "_current_context", None) or {}
        asset_name = context.get("asset_name")
        asset_type = context.get("asset_type")
        for role, role_data in permissions.items():
            members = role_data.get("members", [])
            for member in members:
                yield {
                    "asset_name": asset_name,
                    "role": role,
                    "member": member,
                    "asset_type": asset_type,
                }


class ReportPermissionsStream(_PermissionsStream):
    """Permissions for each report asset (child of ReportsStream)."""

    name = "report_permissions"
    path = "/assets/{asset_name}/permissions"
    parent_stream_type = ReportsStream


class DataSourcePermissionsStream(_PermissionsStream):
    """Permissions for each data source asset (child of DataSourcesStream)."""

    name = "data_source_permissions"
    path = "/assets/{asset_name}/permissions"
    parent_stream_type = DataSourcesStream

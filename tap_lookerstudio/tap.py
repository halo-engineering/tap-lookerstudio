"""TapLookerStudio entry point."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_lookerstudio.streams import (
    DataSourcePermissionsStream,
    DataSourcesStream,
    ReportPermissionsStream,
    ReportsStream,
)


class TapLookerStudio(Tap):
    """Singer tap for Google Looker Studio asset metadata."""

    name = "tap-lookerstudio"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "service_account_json",
            th.ObjectType(),
            required=True,
            description="Google service account key JSON (parsed object)",
        ),
        th.Property(
            "delegated_user_email",
            th.StringType,
            required=True,
            description="Google Workspace user email to impersonate via domain-wide delegation",
        ),
        th.Property(
            "include_trashed",
            th.BooleanType,
            default=False,
            description="Include trashed assets in results",
        ),
        th.Property(
            "owner_filter",
            th.StringType,
            description="Filter assets by owner email",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Initial bookmark for incremental streams",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [
            ReportsStream(self),
            DataSourcesStream(self),
            ReportPermissionsStream(self),
            DataSourcePermissionsStream(self),
        ]


if __name__ == "__main__":
    TapLookerStudio.cli()

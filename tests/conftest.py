"""Shared fixtures for tap-lookerstudio tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_config():
    """Return a minimal valid config for testing."""
    return {
        "service_account_json": {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "key123",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2a2rwplBQLHgVQ+kOBe8mOPCyN0l8MKs5FnBKMSBYMnJYWl8\nqHYsOaF6m3fQ6m3OZSM7oBLaPdGSVGblVKsHC5QLRKG+5mfRHbOIsBjNPC9mDne\njJxBiGKJSTn6dBJLDOCyAoRLSi2fII3sOQjFiIWkGRqUj8YV0o5KzFfCOaeEFll3\nvd6NyNjoCVDgRoACtKKHrhOCjmFCwSFHBXkEB7GIjKJl8caKsGfEOQb0ObNjOT8N\nPN6LX6KJMFfKfBNKdLlSPrAoXJbDBMEycijGl7OAKJFHdNyMrD0V+amLZGbxFicV\nXTBpXC1vbKWlahZ0yOBfvVzxpUWMxOlsCwIDAQABAoIBABfG1w5I6k/gMQoR0j1o\nS/7C/kSH8a72+Ef9l9EvL3b9nMSR9SG2IWLK/K7vdHNL4L+BFexYTwAAhDnbJpKl\nMBAolVQQTUHBEWnNXZ5hDF/qoFIuNKCGX3EYIKDW08c6X/YIKX5VGbNGm6PAWE6D\nLR9m1xkPo8R/MXQG4ZTGnEe4bTYNpTLSCQalFOhGZaXhEe6KkLWmOFkb02GMVFz\nwGYpYOoY2N0EPJY0JRKmXwg8Pt0UPHC+R1bE6niDewKHvCPG3vqK2IjGdqf0K4x0\n80eZ51YXps2JL0bfbf4fBFmNLPbXqSthq7a/i72avR46/dXVnE2vgmmHRhk1JSMH\nJzECgYEA8bq3tEYOBhR8IGxe0FofWyoG4P0y+mQq8Jazyfkn8d9Cg5Ax+QiPUAHX\nVTw+GxxUzOcFpemb+k1F5+3DNFHQCOR/R3ZuWPy+kfb8jkPSEw+j0glIPhSjl2OL\nqjJJYNhZCAU6IkmEONmSS8NjIbR+TERI1SkvWq3r7EEMEfJKNEkCgYEA5nT3tXHg\nvZVUlGiLWjQqG5Y2+0ROZjMAdZB6YSR4Y7ATi/VRG/x/S3e5H6IG5CG2SxGWcbVH\nr/l3mOPfVR+Z4HQAL9K3u6ks7qF0FQ9ri+OWE3iz3Hv6V4t7zBRReM/y26e0BB8s\nlJShg87BAg4B80eW3HiDKkMtiAxnBUxO8ksCgYBSS8f/Y/PBDb9r8b/O2wRLeJZcn\no4b5h9YHjC+KQMOWWL3F1Jf1LZ0A6JKRD5W4nh0O2wYaG0uIFeQo0P5RWL7E2FT2\nvr4QF0hY3GkkOOlwFqEIrVVtXUPfVcWVqnb/p1f/4xKOcr0r0h5C0bWN8HRYOFmD\nOMqOFZJp1tnMxgepiQKBgFRUGJqp1dO0PYS7Go0Yfy6mFWh4dRZKIiJ3ylp7AFNd\n9CUPmJRNjEb2/4bMJLHl2+yt7V/mBW1FTHB/1qGPVb5KHaFD3U1CnD0fbS/S/HE\nfNW6YRhv/KuTdBHfsIMhv4tz3eqr1g7H0VNa5Iu2d0PKVfJmJH5ZYXJEB4NTG4oJ\nAoGBAMRQA0MjClqTG3fyqM5N4Zy3u+DTLd5lFhRQ4+nhnsTxHgBZ5IqU9JmV9+ZL\nbpKjKNL7WHhkT/+4H5ULfJM5EMgwJbcGRUWYPmMRHB5T0RFX5n5iNjm1cGHbcPIw\nmRG0n0eWbA6g//3bQLH0+gPR3ZHf0TH07SfLs2WT/CqBVHCe\n-----END RSA PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        "delegated_user_email": "admin@example.com",
    }


SAMPLE_REPORTS_RESPONSE = {
    "assets": [
        {
            "name": "assets/report1",
            "assetType": "REPORT",
            "title": "Test Report",
            "description": "A test report",
            "owner": "owner@example.com",
            "creator": "creator@example.com",
            "createTime": "2024-01-01T00:00:00Z",
            "updateTime": "2024-06-01T12:00:00Z",
            "trashed": False,
        }
    ]
}

SAMPLE_REPORTS_PAGE1 = {
    "assets": [
        {
            "name": "assets/report1",
            "assetType": "REPORT",
            "title": "Report Page 1",
            "owner": "owner@example.com",
            "creator": "creator@example.com",
            "createTime": "2024-01-01T00:00:00Z",
            "updateTime": "2024-06-01T12:00:00Z",
            "trashed": False,
        }
    ],
    "nextPageToken": "page2token",
}

SAMPLE_REPORTS_PAGE2 = {
    "assets": [
        {
            "name": "assets/report2",
            "assetType": "REPORT",
            "title": "Report Page 2",
            "owner": "owner@example.com",
            "creator": "creator@example.com",
            "createTime": "2024-02-01T00:00:00Z",
            "updateTime": "2024-07-01T12:00:00Z",
            "trashed": False,
        }
    ],
}

SAMPLE_DATA_SOURCES_RESPONSE = {
    "assets": [
        {
            "name": "assets/ds1",
            "assetType": "DATA_SOURCE",
            "title": "Test Data Source",
            "owner": "owner@example.com",
            "creator": "creator@example.com",
            "createTime": "2024-01-01T00:00:00Z",
            "updateTime": "2024-06-01T12:00:00Z",
            "trashed": False,
        }
    ]
}

SAMPLE_PERMISSIONS_RESPONSE = {
    "permissions": {
        "OWNER": {"members": ["user:owner@example.com"]},
        "EDITOR": {"members": ["user:editor1@example.com", "user:editor2@example.com"]},
        "VIEWER": {"members": ["domain:example.com"]},
    }
}

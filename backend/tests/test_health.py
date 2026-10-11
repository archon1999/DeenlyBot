from unittest.mock import patch

import pytest
from django.db import OperationalError


@pytest.mark.django_db
def test_health_is_ready_only_when_database_is_reachable(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_expose_database_error_or_credentials(client):
    with patch("config.urls.connection.cursor", side_effect=OperationalError("private credential")):
        response = client.get("/health/")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "private credential" not in response.content.decode()

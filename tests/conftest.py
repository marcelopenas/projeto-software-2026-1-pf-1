# tests/conftest.py
import os
from unittest.mock import patch

import pytest
from testcontainers.postgres import PostgresContainer

from db import db
from main import create_app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        url = postgres.get_connection_url()

        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://")

        yield url

@pytest.fixture(scope="session")
def app(postgres_container):

    os.environ["SQLALCHEMY_DATABASE_URI"] = postgres_container
    os.environ["TESTING"] = "true"

    flask_app = create_app()
    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    # Mock JWT decorators to bypass authentication in tests
    with patch("main.verify_jwt_in_request"), \
         patch("main.get_jwt", return_value={"https://social-insper.com/roles": ["ADMIN", "USER"]}):
        yield app.test_client()

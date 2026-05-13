import os
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from flask import Flask, Response, jsonify, request
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    get_jwt,
    verify_jwt_in_request,
)
from jwt import PyJWKClient

from db import db
from models import Course

F = TypeVar("F", bound=Callable[..., Any])
P = ParamSpec("P")
T = TypeVar("T", bound=ResponseReturnValue)


def admin_required() -> Callable[[F], F]:
    def wrapper(fn: F) -> F:
        @wraps(fn)
        def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
            verify_jwt_in_request()
            claims = get_jwt()
            # Auth0 custom claims usually require the full namespace URL
            roles = claims.get("https://social-insper.com/roles", [])
            if isinstance(roles, list) and "ADMIN" in roles:
                return fn(*args, **kwargs)
            return cast(
                "T",
                (jsonify(msg="Apenas ADMIN pode executar esta ação"), 403),
            )

        return cast("F", decorator)

    return wrapper


def user_required() -> Callable[[F], F]:
    def wrapper(fn: F) -> F:
        @wraps(fn)
        def decorator(*args: P.args, **kwargs: P.kwargs) -> T:
            verify_jwt_in_request()
            claims = get_jwt()
            roles = claims.get("https://social-insper.com/roles", [])
            if isinstance(roles, list) and (
                "USER" in roles or "ADMIN" in roles
            ):
                return fn(*args, **kwargs)
            return cast(
                "T",
                (jsonify(msg="Apenas USER pode executar esta ação"), 403),
            )

        return cast("F", decorator)

    return wrapper


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=["https://projeto-software-2026-1-pf-2.vercel.app/"])

    postgres_user = os.environ.get("POSTGRES_USER", "appuser")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "apppass")
    postgres_url = os.environ.get("POSTGRES_URL", "localhost")
    postgres_db = os.environ.get("POSTGRES_DB", "database")
    db_uri = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/{postgres_db}"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", db_uri,
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")

    # if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
    #     raise ValueError("AUTH0_DOMAIN and AUTH0_AUDIENCE must be set")

    app.config["JWT_ALGORITHM"] = "RS256"
    app.config["JWT_DECODE_AUDIENCE"] = AUTH0_AUDIENCE
    app.config["JWT_DECODE_ISSUER"] = f"https://{AUTH0_DOMAIN}/"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    jwt_manager = JWTManager(app)
    db.init_app(app)

    jwks_client = PyJWKClient(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")

    @jwt_manager.decode_key_loader
    def decode_key_loader(jwks_header, jwks_payload):
        # print(request.headers.get("Authorization").split(" ")[1])
        signing_key = jwks_client.get_signing_key_from_jwt(
            request.headers.get("Authorization").split(" ")[1],
        )

        return signing_key.key

    @app.route("/courses", methods=["POST"])
    @admin_required()
    def create_course() -> tuple[Response, int]:
        data = request.json
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = ["code", "name", "instructor_name", "date", "status", "instructor_email"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        course = Course(
            code=data["code"],
            name=data["name"],
            instructor_name=data["instructor_name"],
            date=data["date"],
            status=data["status"],
            instructor_email=data["instructor_email"],
        )
        db.session.add(course)
        db.session.commit()
        return jsonify(
            {"id": str(course.id), "code": course.code, "name": course.name},
        ), 201

    @app.route("/courses/<uuid:course_id>", methods=["GET"])
    @user_required()
    def get_course(course_id) -> tuple[Response, int]:
        course = Course.query.get_or_404(course_id)
        return jsonify(
            {"id": str(course.id), "code": course.code, "name": course.name},
        ), 200

    @app.route("/courses", methods=["GET"])
    @user_required()
    def list_courses() -> tuple[Response, int]:
        courses = Course.query.all()
        course_list = [
            {"id": str(course.id), "code": course.code, "name": course.name}
            for course in courses
        ]
        return jsonify(course_list), 200

    @app.route("/courses/<uuid:course_id>", methods=["DELETE"])
    @admin_required()
    def delete_course(course_id) -> tuple[str, int]:
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

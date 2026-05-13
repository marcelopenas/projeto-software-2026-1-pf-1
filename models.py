import enum
import uuid

from db import db


class Status(enum.Enum):
    DISPONIVEL = "DISPONIVEL"
    CANCELADO = "CANCELADO"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(120), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    instructor_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    instructor_email = db.Column(db.String(100), nullable=False)

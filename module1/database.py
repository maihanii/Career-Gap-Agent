
"""Database operations for CV profile management."""

import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, String, DateTime, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from dotenv import load_dotenv
from pathlib import Path

# Load .env from the module1 directory.
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


class Base(DeclarativeBase):
    pass


class CV(Base):
    __tablename__ = "cvs"

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    extracted_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


def initialize_database():
    """Create database tables if they do not exist."""

    Base.metadata.create_all(engine)


def save_cv(filename: str, cv_data: dict) -> int:
    """Save a new CV profile."""

    if not filename:
        raise ValueError("Filename cannot be empty")

    if not isinstance(cv_data, dict):
        raise TypeError("cv_data must be a dictionary")

    with Session(engine) as session:

        cv = CV(
            filename=filename,
            extracted_data=cv_data
        )

        session.add(cv)
        session.commit()
        session.refresh(cv)

        return cv.id


def get_cv(cv_id: int):
    """Retrieve one CV profile by ID."""

    with Session(engine) as session:

        cv = session.get(CV, cv_id)

        if cv is None:
            return None

        return {
            "id": cv.id,
            "filename": cv.filename,
            "extracted_data": cv.extracted_data,
            "created_at": cv.created_at.isoformat()
        }


def get_all_cvs():
    """Retrieve all CV profiles."""

    with Session(engine) as session:

        query = select(CV).order_by(CV.id.desc())
        cvs = session.scalars(query).all()

        return [
            {
                "id": cv.id,
                "filename": cv.filename,
                "extracted_data": cv.extracted_data,
                "created_at": cv.created_at.isoformat()
            }
            for cv in cvs
        ]


def update_cv(cv_id: int, cv_data: dict):
    """Update an existing CV profile."""

    if not isinstance(cv_data, dict):
        raise TypeError("cv_data must be a dictionary")

    with Session(engine) as session:

        cv = session.get(CV, cv_id)

        if cv is None:
            return None

        # Replace the extracted data
        cv.extracted_data = cv_data

        session.commit()

    return get_cv(cv_id)


def delete_cv(cv_id: int) -> bool:
    """Delete a CV profile by ID."""

    with Session(engine) as session:

        cv = session.get(CV, cv_id)

        if cv is None:
            return False

        session.delete(cv)
        session.commit()

        return True

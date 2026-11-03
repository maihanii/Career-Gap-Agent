import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, DateTime, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

class CV(Base):
    __tablename__ = "cvs"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

def initialize_database():
    Base.metadata.create_all(engine)

def save_cv(filename: str, cv_data: dict) -> int:
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

        return cv.id

def get_cv(cv_id: int):
    with Session(engine) as session:
        cv = session.get(CV, cv_id)
        
        if cv is None:
                return None

        return {
            "id": cv.id,
            "filename": cv.filename,
            "extracted_data": cv.extracted_data,
            "created_at": cv.created_at.isoformat(),
        }

def get_all_cvs():
    with Session(engine) as session:
        query = select(CV).order_by(CV.id.desc())
        cvs = session.scalars(query).all()

        return [
            {
                "id": cv.id,
                "filename": cv.filename,
                "extracted_data": cv.extracted_data,
                "created_at": cv.created_at.isoformat(),
            }
            for cv in cvs
        ]
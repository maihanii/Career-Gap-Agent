
"""FastAPI application for CV upload and profile management."""

import os
import tempfile
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool

from database import (
    initialize_database,
    get_cv,
    get_all_cvs,
    update_cv,
    delete_cv
)

from profile_agent import process_cv_file
from schemas import CVSchema


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the API starts."""

    initialize_database()
    logger.info("Database initialized successfully.")

    yield


app = FastAPI(
    title="Career Gap Agent API",
    description="API for uploading CVs and managing extracted profiles.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/cv/upload", status_code=201)
async def upload_cv(file: UploadFile = File(...)):
    """Upload a CV, extract its information, and save the profile."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

    original_filename = file.filename.replace("\\", "/").split("/")[-1]
    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload PDF, DOCX, or TXT."
        )

    file_content = await file.read(MAX_FILE_SIZE + 1)

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 5 MB limit."
        )

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            delete=False
        ) as temp_file:

            temp_file.write(file_content)
            temp_file_path = temp_file.name

        logger.info("Processing uploaded CV: %s", original_filename)

        profile = await run_in_threadpool(
            process_cv_file,
            temp_file_path,
            original_filename
        )

        logger.info(
            "CV processed successfully. ID: %s",
            profile["id"]
        )

        return {
            "message": "CV uploaded and processed successfully.",
            "profile": profile
        }

    except ValueError as error:
        logger.warning("CV validation error: %s", error)

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception:
        logger.exception("Error while processing CV")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the CV."
        )

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        await file.close()


@app.get("/cv")
async def list_cvs():
    """Return all saved CV profiles."""

    try:
        return await run_in_threadpool(get_all_cvs)

    except Exception:
        logger.exception("Could not retrieve CV profiles")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve CV profiles."
        )


@app.get("/cv/{cv_id}")
async def get_cv_by_id(cv_id: int):
    """Return one saved CV profile by its ID."""

    try:
        profile = await run_in_threadpool(get_cv, cv_id)

        if profile is None:
            raise HTTPException(
                status_code=404,
                detail="CV profile not found."
            )

        return profile

    except HTTPException:
        raise

    except Exception:
        logger.exception("Could not retrieve CV ID: %s", cv_id)

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve the CV profile."
        )


@app.put("/cv/{cv_id}")
async def update_cv_profile(cv_id: int, profile_data: CVSchema):
    """Update an existing CV profile."""

    try:
        updated_data = profile_data.model_dump(mode="json")

        result = await run_in_threadpool(
            update_cv,
            cv_id,
            updated_data
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="CV profile not found."
            )

        return {
            "message": "CV profile updated successfully.",
            "profile": result
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Could not update CV ID: %s", cv_id)

        raise HTTPException(
            status_code=500,
            detail="Could not update the CV profile."
        )


@app.delete("/cv/{cv_id}")
async def delete_cv_profile(cv_id: int):
    """Delete an existing CV profile."""

    try:
        result = await run_in_threadpool(delete_cv, cv_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail="CV profile not found."
            )

        return {
            "message": "CV profile deleted successfully.",
            "id": cv_id
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Could not delete CV ID: %s", cv_id)

        raise HTTPException(
            status_code=500,
            detail="Could not delete the CV profile."
        )

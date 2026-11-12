
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
import api


@pytest.fixture
def client(monkeypatch):
    # Prevent connecting to the real database during tests
    monkeypatch.setattr(api, "initialize_database", lambda: None)

    with TestClient(api.app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_cvs(client, monkeypatch):
    fake_cvs = [
        {"id": 1, "filename": "Mai_CV.pdf"},
        {"id": 2, "filename": "Test_CV.pdf"}
    ]

    monkeypatch.setattr(api, "get_all_cvs", lambda: fake_cvs)

    response = client.get("/cv")

    assert response.status_code == 200
    assert response.json() == fake_cvs


def test_get_existing_cv(client, monkeypatch):
    fake_profile = {
        "id": 1,
        "filename": "Mai_CV.pdf"
    }

    monkeypatch.setattr(
        api,
        "get_cv",
        lambda cv_id: fake_profile if cv_id == 1 else None
    )

    response = client.get("/cv/1")

    assert response.status_code == 200
    assert response.json() == fake_profile


def test_get_nonexistent_cv(client, monkeypatch):
    monkeypatch.setattr(api, "get_cv", lambda cv_id: None)

    response = client.get("/cv/999")

    assert response.status_code == 404


def test_upload_unsupported_file(client):
    response = client.post(
        "/cv/upload",
        files={"file": ("test.jpg", b"image content", "image/jpeg")}
    )

    assert response.status_code == 400


def test_upload_empty_file(client):
    response = client.post(
        "/cv/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )

    assert response.status_code == 400


def test_upload_large_file(client):
    large_content = b"x" * (api.MAX_FILE_SIZE + 1)

    response = client.post(
        "/cv/upload",
        files={"file": ("large.pdf", large_content, "application/pdf")}
    )

    assert response.status_code == 413


def test_upload_success(client, monkeypatch):
    fake_profile = {
        "id": 123,
        "filename": "Mai_CV.pdf",
        "extracted_data": {"skills": ["Python"]}
    }

    monkeypatch.setattr(
        api,
        "process_cv_file",
        lambda file_path, original_filename: fake_profile
    )

    response = client.post(
        "/cv/upload",
        files={
            "file": (
                "Mai_CV.pdf",
                b"Fake PDF content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == (
        "CV uploaded and processed successfully."
    )
    assert response.json()["profile"] == fake_profile


def test_upload_processing_error(client, monkeypatch):
    def fake_process(file_path, original_filename):
        raise ValueError("Could not extract CV text.")

    monkeypatch.setattr(api, "process_cv_file", fake_process)

    response = client.post(
        "/cv/upload",
        files={
            "file": (
                "Mai_CV.pdf",
                b"Fake PDF content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Could not extract CV text."


def test_update_existing_cv(client, monkeypatch):
    updated_profile = {
        "id": 1,
        "filename": "Mai_CV.pdf",
        "extracted_data": {
            "personal_info": {"name": "Mai"},
            "skills": ["Python"]
        }
    }

    monkeypatch.setattr(
        api,
        "update_cv",
        lambda cv_id, data: updated_profile
    )

    response = client.put(
        "/cv/1",
        json={
            "personal_info": {"name": "Mai"},
            "skills": ["Python"]
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "CV profile updated successfully."


def test_update_nonexistent_cv(client, monkeypatch):
    monkeypatch.setattr(
        api,
        "update_cv",
        lambda cv_id, data: None
    )

    response = client.put(
        "/cv/999",
        json={"skills": ["Python"]}
    )

    assert response.status_code == 404


def test_delete_existing_cv(client, monkeypatch):
    monkeypatch.setattr(
        api,
        "delete_cv",
        lambda cv_id: True
    )

    response = client.delete("/cv/1")

    assert response.status_code == 200
    assert response.json()["message"] == "CV profile deleted successfully."


def test_delete_nonexistent_cv(client, monkeypatch):
    monkeypatch.setattr(
        api,
        "delete_cv",
        lambda cv_id: False
    )

    response = client.delete("/cv/999")

    assert response.status_code == 404

import io
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.database.models import State
from api.database.repository import DBJobRepository
from api.database.session import Base, get_db
from api.main import app

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

connection = engine.connect()
TestingSession = sessionmaker(bind=connection, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=connection)
    yield
    Base.metadata.drop_all(bind=connection)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def make_png_bytes(text="hello world") -> bytes:
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_file(
    filename="test.png", content: bytes | None = None, content_type="image/png"
):
    return (filename, content or make_png_bytes(), content_type)


def post_send(client, *files):
    return client.post(
        "/send",
        files=[("files", f) for f in files],
    )


def test_send_single_file_returns_job(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        res = post_send(client, make_file())
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert "job_id" in data[0]
    assert data[0]["filename"] == "test.png"


def test_send_multiple_files_returns_multiple_jobs(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        res = post_send(client, make_file("a.png"), make_file("b.png"))
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_send_creates_job_with_pending_status(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        res = post_send(client, make_file())
    job_id = res.json()[0]["job_id"]
    status_res = client.get(f"/jobs/{job_id}")
    assert status_res.json()["status"] == "pending"


def test_send_disallowed_type_returns_415(client):
    with patch(
        "api.routes.witchtr_router.magic.from_buffer", return_value="text/plain"
    ):
        res = post_send(client, make_file("evil.txt", b"not an image", "text/plain"))
    assert res.status_code == 415


def test_send_pdf_allowed(client):
    pdf_bytes = b"%PDF-1.4 fake pdf content"
    with (
        patch(
            "api.routes.witchtr_router.magic.from_buffer",
            return_value="application/pdf",
        ),
        patch("api.routes.witchtr_router.run_job"),
    ):
        res = post_send(client, make_file("doc.pdf", pdf_bytes, "application/pdf"))
    assert res.status_code == 200


def test_send_no_files_returns_422(client):
    res = client.post("/send", files=[])
    assert res.status_code == 422


def test_send_job_ids_are_unique(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        res = post_send(client, make_file("a.png"), make_file("b.png"))
    ids = [j["job_id"] for j in res.json()]
    assert ids[0] != ids[1]


def test_send_job_id_is_valid_uuid(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        res = post_send(client, make_file())
    job_id = res.json()[0]["job_id"]
    uuid.UUID(job_id)


def test_job_status_pending(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    res = client.get(f"/jobs/{job_id}")
    assert res.status_code == 200
    assert res.json()["status"] == "pending"


def test_job_status_not_found(client):
    res = client.get(f"/jobs/{uuid.uuid4()}")
    assert res.status_code == 404


def test_job_status_has_expected_keys(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    res = client.get(f"/jobs/{job_id}")
    data = res.json()
    assert "job_id" in data and "status" in data and "error" in data


def test_job_status_done_after_update(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    db = TestingSession()
    DBJobRepository(db).update_job(job_id, State.DONE, result={"text": "hello"})
    db.close()
    res = client.get(f"/jobs/{job_id}")
    assert res.json()["status"] == "done"


def test_job_status_error_after_update(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    db = TestingSession()
    DBJobRepository(db).update_job(job_id, State.ERROR, error="something failed")
    db.close()
    res = client.get(f"/jobs/{job_id}")
    data = res.json()
    assert data["status"] == "error"
    assert data["error"] == "something failed"


def test_get_result_not_found(client):
    res = client.get(f"/jobs/{uuid.uuid4()}/result")
    assert res.status_code == 404


def test_get_result_pending_returns_202(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    res = client.get(f"/jobs/{job_id}/result")
    assert res.status_code == 202


def test_get_result_running_returns_202(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    db = TestingSession()
    DBJobRepository(db).update_job(job_id, State.RUNNING)
    db.close()
    res = client.get(f"/jobs/{job_id}/result")
    assert res.status_code == 202


def test_get_result_done_returns_result(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    db = TestingSession()
    DBJobRepository(db).update_job(job_id, State.DONE, result={"text": "hello world"})
    db.close()
    res = client.get(f"/jobs/{job_id}/result")
    assert res.status_code == 200
    data = res.json()
    assert data["result"] == {"text": "hello world"}
    assert data["job_id"] == job_id


def test_get_result_done_has_expected_keys(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    db = TestingSession()
    DBJobRepository(db).update_job(job_id, State.DONE, result={"text": "ok"})
    db.close()
    res = client.get(f"/jobs/{job_id}/result")
    data = res.json()
    assert all(k in data for k in ["job_id", "status", "error", "result"])


def test_get_result_error_state_returns_202(client):
    with (
        patch("api.routes.witchtr_router.magic.from_buffer", return_value="image/png"),
        patch("api.routes.witchtr_router.run_job"),
    ):
        job_id = post_send(client, make_file()).json()[0]["job_id"]
    db = TestingSession()
    DBJobRepository(db).update_job(job_id, State.ERROR, error="ocr failed")
    db.close()
    res = client.get(f"/jobs/{job_id}/result")
    assert res.status_code == 202

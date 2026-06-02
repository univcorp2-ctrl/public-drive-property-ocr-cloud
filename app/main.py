from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import db
from app.config import get_settings
from app.services.auth import is_note_id_allowed, normalize_note_id
from app.services.exporter import export_result
from app.services.ocr import extract_text
from app.services.volume import analyze_volume

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class SessionRequest(BaseModel):
    note_id: str


@app.on_event("startup")
def startup() -> None:
    db.init_db()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/config")
def config() -> dict[str, object]:
    return {
        "app_name": settings.app_name,
        "liff_id": settings.liff_id,
        "note_auth_mode": settings.note_auth_mode,
        "demo_note_ids": sorted(settings.allowlist) if settings.note_auth_mode == "allowlist" else [],
    }


@app.post("/api/session")
def create_session(payload: SessionRequest) -> dict[str, str]:
    note_id = normalize_note_id(payload.note_id)
    if not is_note_id_allowed(note_id):
        raise HTTPException(status_code=403, detail="note ID is not allowed")
    token = uuid4().hex
    db.create_session(token, note_id)
    return {"token": token, "note_id": note_id}


@app.post("/api/analyze")
async def analyze(
    token: str = Form(...),
    file: UploadFile = File(...),
    manual_text: str = Form(""),
) -> dict[str, object]:
    session = db.get_session(token)
    if session is None:
        raise HTTPException(status_code=401, detail="invalid session token")

    job_id = uuid4().hex
    safe_name = Path(file.filename or "upload.bin").name
    upload_path = settings.upload_dir / f"{job_id}_{safe_name}"
    content = await file.read()
    upload_path.write_bytes(content)

    extracted_text = extract_text(upload_path, manual_text=manual_text)
    result = analyze_volume(extracted_text)
    output_dir = settings.output_dir / job_id
    export_result(job_id, output_dir, result, extracted_text)

    db.create_job(
        job_id=job_id,
        token=token,
        note_id=session["note_id"],
        upload_name=safe_name,
        extracted_text=extracted_text,
        result=result,
        output_dir=output_dir,
    )

    return {
        "job_id": job_id,
        "result": result,
        "exports": {
            "csv": f"/api/jobs/{job_id}/exports/csv",
            "xlsx": f"/api/jobs/{job_id}/exports/xlsx",
            "txt": f"/api/jobs/{job_id}/exports/txt",
        },
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    job = db.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/api/jobs/{job_id}/exports/{kind}")
def download_export(job_id: str, kind: str) -> FileResponse:
    if kind not in {"csv", "xlsx", "txt"}:
        raise HTTPException(status_code=404, detail="unsupported export type")
    job = db.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")

    path = Path(job["output_dir"]) / f"{job_id}.{kind}"
    if not path.exists():
        raise HTTPException(status_code=404, detail="export not found")

    media_types = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "txt": "text/plain",
    }
    return FileResponse(path, media_type=media_types[kind], filename=path.name)

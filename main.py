from typing import Annotated
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
import aiofiles
from pathlib import Path
from sqlmodel import Session, select
from contextlib import asynccontextmanager

from database import Filedb, create_db_and_tables, get_session

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload/stream")
async def upload_stream(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    target = UPLOAD_DIR / file.filename

    if file.content_type not in {"image/png", "image/jpeg"}:
       raise HTTPException(415, "Unsupported file type")

    async with aiofiles.open(target, "wb") as out:
        while chunk := await file.read(1024*1024):
            await out.write(chunk)

    new_file = Filedb(file_rg=str(target))
    session.add(new_file)
    session.commit()
    session.refresh(new_file)

    return {
      "id": new_file.id,
      "stored_as": new_file.file_rg
    }

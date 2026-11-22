from typing import Annotated
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, Response
from fastapi.responses import FileResponse
import aiofiles
from pathlib import Path
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from database import Filedb, create_db_and_tables, get_session

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
app = FastAPI(lifespan=lifespan)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def homepage(request: Request) -> Response:
    names = [archive.name for archive in Path("uploads").iterdir() if archive.is_file()]
    return templates.TemplateResponse(request, "index.html", {"photos": names})

@app.get("/search")
async def read_item(q: str):
  upload_folder = Path("uploads")
  archive = upload_folder / q
  
  if archive.is_file():
     return {"Exists": True, "archive": q}
  else:
     return {"Exists": False, "archive": q}

@app.get("/download/{filename}")
async def download_file(filename: str):
  archive = UPLOAD_DIR / filename

  if not archive.is_file():
      raise HTTPException(status_code=404, detail="Archive doesn't exists")
  return FileResponse(path=archive, filename=filename)
    


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

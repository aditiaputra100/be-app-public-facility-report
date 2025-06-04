import os
import shutil
from fastapi import FastAPI, Depends, Form, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from dependency.auth import get_current_user
from models import Report, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.post("/report")
async def create_report(
        facility: str = Form(),
        description: str = Form(),
        location: str = Form(),
        picture: UploadFile = File(),
        db: Session = Depends(get_db),
        # user_id: str = Form(...)
        user: dict = Depends(get_current_user)
):

    if picture.filename == "":
        raise HTTPException(400, detail="No image uploaded")

    if facility == "":
        raise HTTPException(400, detail="Facility cannot be empty string")

    file_path = f"uploads/{picture.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(picture.file, buffer)

    report = Report(
        user_uid = user["uid"],
        # user_uid = user_id,
        facility = facility,
        description = description,
        location = location,
        picture_path = file_path
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {"msg": "Success created report", "id": report.id}

@app.get("/report")
async def get_report(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    pass

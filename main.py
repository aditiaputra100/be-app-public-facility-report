import os
import shutil
from fastapi import FastAPI, Depends, Form, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from dependency.auth import get_current_user, get_current_admin
from models import Report, User, Admin, Base
from firebase_admin.auth import UserRecord

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.post("/register/user", status_code=status.HTTP_201_CREATED)
def create_user(user:UserRecord = Depends(get_current_user), db: Session = Depends(get_db)):
    print(user)

    user = User(
        uid = user.uid,
        full_name = user.display_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "msg": "Success created user",
        "uid": user.uid
    }

@app.post("/register/admin", status_code=status.HTTP_201_CREATED)
def create_admin(user: UserRecord = Depends(get_current_admin), db: Session = Depends(get_db)):
    admin = Admin(
        uid = user.uid,
        full_name = user.display_name
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return {
        "msg": "Success created user",
        "uid": admin.uid
    }


@app.post("/report", status_code=status.HTTP_201_CREATED)
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

@app.get("/report", dependencies=[Depends(get_current_user)])
async def get_report(db: Session = Depends(get_db)):
    report = db.query(models.Report).all()

    return {
        "data": report
    }

@app.get("/report/user/{uid}", dependencies=[Depends(get_current_user)])
async def get_report_by_user_uid(uid: str, db: Session = Depends(get_db)):
    report = db.query(models.Report).where(uid == models.Report.user_uid).all()

    print(report)


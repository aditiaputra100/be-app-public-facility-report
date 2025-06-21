import os
import shutil
from fastapi import FastAPI, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
import models
import schemas
from database import engine, get_db
from dependency.auth import get_current_user, get_current_admin, get_current_user_or_admin
from models import Report, User, Admin, Base
from firebase_admin.auth import UserRecord

Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def read_root():
    return {"msg": "Hello World"}

@app.get("/uploads/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path, media_type="image/jpeg")

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
        user: UserRecord = Depends(get_current_user)
):

    if picture.filename == "":
        raise HTTPException(400, detail="No image uploaded")

    if facility == "":
        raise HTTPException(400, detail="Facility cannot be empty string")

    file_path = f"uploads/{picture.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(picture.file, buffer)

    report = Report(
        user_uid = user.uid,
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
    # return {"msg": "Success created report"}

@app.get("/report", dependencies=[Depends(get_current_user_or_admin)], response_model=schemas.ReportListResponse)
async def get_report(db: Session = Depends(get_db), limit: int = 10):
    reports = db.query(models.Report).options(joinedload(models.Report.user), joinedload(models.Report.admin)).limit(limit).all()

    in_review: int = 0
    in_progress: int = 0
    in_finished: int = 0

    for report in reports:
        if report.status == "in-review":
            in_review += 1
        elif report.status == "in-progress":
            in_progress += 1
        else:
            in_finished += 1

    # return {
    #     "data": reports,
    #     "length": len(reports)
    # }

    return schemas.ReportListResponse(data=[schemas.ReportOut.from_orm(report) for report in reports], length=len(reports), length_review=in_review, length_progress=in_progress, length_finished=in_finished)

@app.get("/report/user/{uid}", dependencies=[Depends(get_current_user)])
async def get_report_by_user_uid(uid: str, db: Session = Depends(get_db)):
    report = db.query(models.Report).where(uid == models.Report.user_uid).all()
    report_length : int = len(report)

    return {
        "data": report,
        "length": report_length
    }

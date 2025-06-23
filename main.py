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

@app.post("/register/admin", dependencies=[Depends(get_current_admin)], status_code=status.HTTP_201_CREATED)
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

@app.get("/admin", dependencies=[Depends(get_current_admin)])
def get_admin(db: Session = Depends(get_db)):
    admins = db.query(models.Admin).all()

    return {
        "data": admins,
        "length": len(admins)
    }


@app.post("/report", dependencies=[Depends(get_current_user)], status_code=status.HTTP_201_CREATED)
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
async def get_report(db: Session = Depends(get_db), status_report: str = "", limit: int = 10):

    if status_report == "":
        reports = db.query(models.Report).options(joinedload(models.Report.user), joinedload(models.Report.admin)).limit(limit).all()
    else:
        reports = db.query(models.Report).options(joinedload(models.Report.user),
                                                  joinedload(models.Report.admin)).where(models.Report.status == status_report).limit(limit).all()

    length_all: int = db.query(models.Report).count()
    length_in_review: int = db.query(models.Report).where(models.Report.status == "in-review").count()
    length_in_progress: int = db.query(models.Report).where(models.Report.status == "in-progress").count()
    length_in_finished: int = db.query(models.Report).where(models.Report.status == "finished").count()

    # return {
    #     "data": reports,
    #     "length": len(reports)
    # }

    return schemas.ReportListResponse(data=[schemas.ReportOut.from_orm(report) for report in reports], counts={
        "all": length_all,
        "in-review": length_in_review,
        "in-progress": length_in_progress,
        "finished": length_in_finished
    })

@app.get("/report/user/{uid}", dependencies=[Depends(get_current_user)])
async def get_report_by_user_uid(uid: str, db: Session = Depends(get_db)):
    report = db.query(models.Report).where(uid == models.Report.user_uid).all()
    report_length : int = len(report)

    return {
        "data": report,
        "length": report_length
    }

@app.put("/report/status/{id}", dependencies=[Depends(get_current_admin)])
async def update_report_status(id: int, status_report: schemas.ReportUpdateStatus, db: Session = Depends(get_db)):
    report = db.query(models.Report).where(models.Report.id == id).first()

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if not status_report:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status cannot be null or empty")

    report.status = status_report.status_report

    db.commit()
    db.refresh(report)

    return {
        "msg": "Update report status successfully",
        "id": report.id
    }
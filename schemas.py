import datetime
from typing import List

from pydantic import BaseModel

class AdminOut(BaseModel):
    uid: str
    full_name: str

    class Config:
        from_attributes=True

class UserOut(BaseModel):
    uid: str
    full_name: str

    class Config:
        from_attributes = True

class ReportOut(BaseModel):
    id: int
    facility: str
    description: str
    location: str
    picture_path: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user: UserOut | None
    admin: AdminOut | None

    class Config:
        from_attributes=True

class ReportListResponse(BaseModel):
    data: List[ReportOut]
    counts: dict[str, int]
    
class ReportUpdateStatus(BaseModel):
    status_report: str
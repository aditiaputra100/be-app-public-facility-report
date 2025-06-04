from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(128), index=True)
    facility = Column(String(255))
    description = Column(Text)
    location = Column(String(255))
    picture_path = Column(String(255))


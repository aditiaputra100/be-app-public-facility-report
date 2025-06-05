from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

class Admin(Base):
    __tablename__ = "admin"
    uid = Column(String(255), primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)

    report = relationship("Report", back_populates="admin")

class User(Base):
    __tablename__ = "user"
    uid = Column(String(255), primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)

    report = relationship("Report", back_populates="user")

class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(128), ForeignKey("user.uid"))
    employee_uid = Column(String(128), ForeignKey("admin.uid"))
    facility = Column(String(255))
    description = Column(Text)
    location = Column(String(255))
    picture_path = Column(String(255))
    status = Column(String(128), default="in-review")
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="report")
    admin = relationship("Admin", back_populates="report")

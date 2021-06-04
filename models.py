from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from database import Base


class family_member(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, unique=True, index=True)


class recipient_record(Base):
    __tablename__ = "recipient_records"

    year = Column(Integer, primary_key=True, index=True)
    record = Column(JSON, unique=False, index=True)
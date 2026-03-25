from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class MedicalReminder(Base):
    __tablename__ = "medical_reminders"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    remind_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
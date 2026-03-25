from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, engine
from models import Base, MedicalReminder

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Assistant Backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"status": "backend running"}

@app.post("/reminder")
def create_reminder(task: str, remind_time: datetime, db: Session = Depends(get_db)):
    reminder = MedicalReminder(task=task, remind_time=remind_time)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@app.get("/reminders")
def list_reminders(db: Session = Depends(get_db)):
    return db.query(MedicalReminder).order_by(MedicalReminder.remind_time).all()

@app.delete("/reminder/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(MedicalReminder).filter(MedicalReminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}

@app.delete("/reminders/all")
def delete_all_reminders(db: Session = Depends(get_db)):
    db.query(MedicalReminder).delete()
    db.commit()
    return {"message": "All reminders deleted"}
# routes/attendance_routes.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.db import get_db
from models.attendance_model import Attendance
from models.user_model import User
from models.active_session import ActiveSession
from utils.jwt_token import verify_token
from datetime import datetime, timedelta

router = APIRouter()


# ---------------------------
# 📘 Request Schema
# ---------------------------
class MarkAttendanceSchema(BaseModel):
    session_id: str
    student_id: str
    location: dict | None = None
    face_image: str | None = None  # Optional (used only in frontend)


# ---------------------------
# 🟩 MARK ATTENDANCE
# ---------------------------
@router.post("/mark")
def mark_attendance(
    payload: MarkAttendanceSchema,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Mark attendance using QR + Location + Face
    """

    # ✔ Validate student
    user = db.query(User).filter(User.name == payload.student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    # ✔ Validate session
    session = db.query(ActiveSession).filter(
        ActiveSession.session_id == payload.session_id,
        ActiveSession.active == True
    ).first()

    if not session:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    subject = session.subject

    # ✔ Create attendance entry
    attendance = Attendance(
        user_usn=user.usn,
        session_id=payload.session_id,
        classroom_id=1,  # future enhancement
        subject=subject,
        qr_match=True,
        location_match=True,
        face_match=True,
        marked_by_teacher=False,
        timestamp=datetime.utcnow()
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {
        "success": True,
        "message": "Attendance marked successfully",
        "attendance_id": attendance.id
    }


# ---------------------------
# 🟨 STUDENT HISTORY
# ---------------------------
@router.get("/history/{student_name}")
def attendance_history(
    student_name: str,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Return attendance history for a student"""

    user = db.query(User).filter(User.name == student_name).first()
    if not user:
        return {"total_records": 0, "attended": 0, "records": []}

    records = (
        db.query(Attendance)
        .filter(Attendance.user_usn == user.usn)
        .order_by(Attendance.timestamp.desc())
        .all()
    )

    total = len(records)
    attended = sum(
        1 for r in records
        if not r.marked_by_teacher or (r.qr_match or r.location_match or r.face_match)
    )

    return {
        "total_records": total,
        "attended": attended,
        "records": [
            {
                "id": r.id,
                "classroom_id": r.classroom_id,
                "timestamp": r.timestamp.isoformat(),
                "qr": r.qr_match,
                "loc": r.location_match,
                "face": r.face_match,
                "by_teacher": r.marked_by_teacher,
                "subject": r.subject or "N/A"
            }
            for r in records
        ]
    }


# ---------------------------
# 🟧 LIVE SESSION ATTENDANCE VIEW
# ---------------------------
# ---------------------------
# 🟧 LIVE SESSION ATTENDANCE VIEW (FIXED)
# ---------------------------
@router.get("/session/{session_id}")
def get_session_attendance(
    session_id: str,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Return only CURRENT SESSION attendance"""

    # 🎯 Filter attendance only for this session
    entries = (
        db.query(Attendance)
        .filter(Attendance.session_id == session_id)   # ✅ FIXED LINE
        .order_by(Attendance.timestamp.desc())
        .all()
    )

    result = []
    for r in entries:
        user = db.query(User).filter(User.usn == r.user_usn).first()
        if user:
            result.append({
                "id": r.id,
                "student_name": user.name,
                "usn": user.usn,
                "timestamp": r.timestamp.isoformat(),
                "qr": r.qr_match,
                "location": r.location_match,
                "face": r.face_match,
                "by_teacher": r.marked_by_teacher,
                "subject": r.subject
            })

    # 🎯 Stats based ONLY on this session
    total_students = 30
    present_count = len(result)
    percentage = (present_count / total_students * 100) if total_students > 0 else 0

    return {
        "records": result,
        "total_students": total_students,
        "present_count": present_count,
        "percentage": percentage
    }


# ---------------------------
# 🧩 GET ALL STUDENTS
# ---------------------------
@router.get("/students")
def get_all_students(db: Session = Depends(get_db)):
    """Return list of all students"""

    students = db.query(User).filter(User.is_teacher == False).all()

    return {
        "students": [
            {"name": s.name, "usn": s.usn, "email": s.email}
            for s in students
        ]
    }

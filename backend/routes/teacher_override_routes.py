# routes/teacher_override_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.db import get_db
from utils.jwt_token import verify_token
from models.user_model import User
from models.attendance_model import Attendance
from datetime import datetime

router = APIRouter()


@router.get("/students")
def list_students(token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Return all students."""
    students = db.query(User).filter(User.is_teacher == False).all()
    return {
        "students": [
            {"name": s.name, "usn": s.usn, "email": s.email}
            for s in students
        ]
    }


@router.post("/mark")
def manual_mark_attendance(
    data: dict,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Teacher manually marks attendance for MULTIPLE students.

    Expected JSON:
    {
        "subject": "Theory of Computation",
        "usns": ["1AM23CS180", "1AM23CS181"],
        "classroom_id": 1
    }
    """

    try:
        subject = data.get("subject")
        usns = data.get("usns", [])
        classroom_id = data.get("classroom_id", 1)

        if not subject:
            raise HTTPException(status_code=400, detail="Subject missing")

        if not usns:
            raise HTTPException(status_code=400, detail="No students provided")

        # ---------------------------------------------------
        # ✅ Create manual session_id (required by Attendance)
        # ---------------------------------------------------
        teacher_usn = token.get("usn")
        manual_session_id = f"manual-{teacher_usn}-{subject.replace(' ', '_')}"
        # ---------------------------------------------------

        marked = []

        for usn in usns:
            user = db.query(User).filter(User.usn == usn).first()
            if not user:
                continue  # skip invalid USN

            att = Attendance(
                user_usn=usn,
                session_id=manual_session_id,    # ✅ FIXED
                classroom_id=classroom_id,
                subject=subject,
                qr_match=False,
                location_match=False,
                face_match=False,
                marked_by_teacher=True,
                timestamp=datetime.utcnow()
            )

            db.add(att)
            marked.append(usn)

        db.commit()

        return {
            "success": True,
            "marked": marked,
            "session_id": manual_session_id,
            "message": "Attendance overridden successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

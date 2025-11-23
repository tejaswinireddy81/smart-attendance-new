from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.db import get_db
from utils.jwt_token import verify_token
from models.teacher_model import Teacher
from models.user_model import User

router = APIRouter()

@router.get("/subjects")
def get_teacher_subjects(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    # token contains teacher USN
    teacher_usn = token.get("usn")

    user = db.query(User).filter(User.usn == teacher_usn).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    teacher = db.query(Teacher).filter(Teacher.user_id == user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    return {"subjects": teacher.subjects_taken or []}

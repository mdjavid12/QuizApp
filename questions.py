from pydantic import BaseModel
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from models import Question
from database import get_db
from auth import admin_required
from fastapi import APIRouter
router = APIRouter(prefix = "/questions")

class QuestionCreate(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

@router.post("")
def create_question(data: QuestionCreate, db: Session = Depends(get_db), user=Depends(admin_required)):
    q = Question(
        question=data.question,
        options=data.options,
        correct_answer=data.correct_answer
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.get("")
def list_questions(db: Session = Depends(get_db), user=Depends(admin_required)):
    return db.query(Question).all()

@router.get("/{id}")
def get_question(id: int, db: Session = Depends(get_db), user=Depends(admin_required)):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(404)
    return q

@router.delete("/{id}")
def delete_question(id: int, db: Session = Depends(get_db), user=Depends(admin_required)):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(404)
    db.delete(q)
    db.commit()
    return {"message": "Deleted"}

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import random

from database import get_db
from models import Question, Result
from auth import get_current_user

router = APIRouter(prefix="/quiz")

@router.get("")
def get_quiz(db: Session = Depends(get_db), user=Depends(get_current_user)):
    questions = db.query(Question).all()
    if not questions:
        raise HTTPException(status_code=400, detail="No questions available")
    
    num_questions = min(2, len(questions))
    selected = random.sample(questions, num_questions)
    
    
    return [
        {
            "id": q.id,
            "question": q.question,
            "options": q.options
        }
        for q in selected
    ]

@router.post("/result")
def submit_quiz(answers: dict[str, str], db: Session = Depends(get_db), user=Depends(get_current_user)):
    score = 0
    correct = {}

    for qid, ans in answers.items():
        q = db.query(Question).filter(Question.id == int(qid)).first()
        if not q:
            continue

        correct[qid] = q.correct_answer
        if ans == q.correct_answer:
            score += 1

    result = Result(user_id=user.id, score=score, total=len(answers))
    db.add(result)
    db.commit()

    return {
        "score": score,
        "total": len(answers),
        "correctAnswers": correct
    }
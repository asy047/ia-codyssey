from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Question


router = APIRouter(
    prefix='/api/question',
    tags=['question'],
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/list', response_model=List[Dict[str, Any]])
def question_list(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    데이터베이스에 저장된 질문 목록을 ORM 을 이용해서 가져온다.
    """
    questions = db.query(Question).order_by(Question.id.desc()).all()

    result: List[Dict[str, Any]] = []

    for question in questions:
        result.append(
            {
                'id': question.id,
                'subject': question.subject,
                'content': question.content,
                'create_date': question.create_date.isoformat(),
            },
        )

    return result

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Question


router = APIRouter(
    prefix='/api/question',
    tags=['question'],
)


class QuestionSchema(BaseModel):
    """
    질문 응답에 사용할 Pydantic 스키마.
    """

    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        # 보너스 과제:
        # orm_mode = False 로 바꾸면 ORM 객체(Question)를 그대로 리턴할 때
        # 속성을 dict 처럼 찾지 못해서 ValidationError 가 발생한다.
        # orm_mode = True 이면 Pydantic 이 ORM 모델의 속성을
        # 객체 속성 접근 방식으로 읽어와서 직렬화해 준다.
        orm_mode = True


@router.get('/list', response_model=List[QuestionSchema])
def question_list(db: Session = Depends(get_db)) -> List[Question]:
    """
    SQLite 에 저장된 질문 목록을 ORM 을 사용해서 조회한다.
    """
    questions = db.query(Question).order_by(Question.id.desc()).all()
    return questions




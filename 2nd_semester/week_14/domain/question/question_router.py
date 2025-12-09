from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
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
        orm_mode = True


class QuestionCreate(BaseModel):
    """
    질문 등록에 사용할 Pydantic 스키마.

    제목(subject)과 내용(content)은 빈 문자열을 허용하지 않는다.
    """

    subject: str = Field(
        ...,
        min_length=1,
        description='질문의 제목 (빈 값 불가)',
    )
    content: str = Field(
        ...,
        min_length=1,
        description='질문의 내용 (빈 값 불가)',
    )


@router.get('/list', response_model=List[QuestionSchema])
def question_list(db: Session = Depends(get_db)) -> List[Question]:
    """
    SQLite 에 저장된 질문 목록을 ORM 을 사용해서 조회한다.
    """
    questions = db.query(Question).order_by(Question.id.desc()).all()
    return questions


@router.post('/create', response_model=QuestionSchema)
def question_create(
    question_create: QuestionCreate,
    db: Session = Depends(get_db),
) -> Question:
    """
    SQLite 에 질문을 등록하는 API.

    - POST 메서드를 사용한다.
    - Depends(get_db) 를 사용해서 데이터베이스 연결을 관리한다.
    - ORM(Question 모델)을 사용해 데이터를 저장한다.
    """
    question = Question(
        subject=question_create.subject,
        content=question_create.content,
        create_date=datetime.utcnow(),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question





from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Question
from domain.question.question_router import router as question_router


# Alembic 으로 테이블을 관리하는 것이 원칙.
# 초기 개발 단계에서만 사용하려면 주석 해제 가능.
# Base.metadata.create_all(bind=engine)


app = FastAPI(
    title='Mars Board API',
    description='문제5/6 게시판 + 질문 기능 - SQLite + SQLAlchemy + FastAPI',
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def read_root() -> Dict[str, str]:
    return {'message': 'Mars Board API is running'}


@app.get('/questions', response_model=List[Dict[str, Any]])
def list_questions(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    기존 문제5에서 사용하던 예시용 질문 목록 API.
    (원하면 삭제해도 무방, /api/question/list 를 사용해도 됨)
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


@app.post('/questions', response_model=Dict[str, Any])
def create_question(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    질문 생성용 예시 API.
    """
    subject = str(data.get('subject', '')).strip()
    content = str(data.get('content', '')).strip()

    if not subject:
        raise HTTPException(
            status_code=400,
            detail='subject 는 빈 값일 수 없습니다.',
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail='content 는 빈 값일 수 없습니다.',
        )

    question = Question(
        subject=subject,
        content=content,
        create_date=datetime.utcnow(),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        'id': question.id,
        'subject': question.subject,
        'content': question.content,
        'create_date': question.create_date.isoformat(),
    }


# ★ 문제6 요구사항: question 라우터 등록
app.include_router(question_router)

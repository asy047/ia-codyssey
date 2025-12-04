from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Question


# 초기용: Alembic 사용 전 테스트할 때는 아래 주석을 해제해서 테이블 생성 가능
# 실제 과제에서는 alembic 으로 마이그레이션을 수행하는 것이 핵심.
# Base.metadata.create_all(bind=engine)


app = FastAPI(
    title='Mars Board API',
    description='문제5 데이터베이스를 또… - SQLite + SQLAlchemy + FastAPI',
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

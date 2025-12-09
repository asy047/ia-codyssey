from datetime import datetime
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Question
from domain.question.question_router import router as question_router


# 초기 개발 단계에서만 사용하는 테이블 생성 코드.
# 실제 운영 시에는 Alembic 과 같은 마이그레이션 도구를 사용하는 것이 일반적이다.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title='Mars Board API - Week 13',
    description='문제7 질문 기능 - contextlib 기반 의존성 주입 + Pydantic 스키마',
)


@app.get('/')
def read_root() -> Dict[str, str]:
    return {'message': 'Mars Board API (week_13) is running'}


@app.get('/questions', response_model=List[Dict[str, Any]])
def list_questions(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    예시용 질문 목록 API.
    /api/question/list 와 유사한 기능을 제공한다.
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
    질문 생성 예시 API.
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


# 문제7 요구사항: question 라우터 등록
app.include_router(question_router)




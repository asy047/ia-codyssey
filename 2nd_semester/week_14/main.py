from typing import Dict

from fastapi import FastAPI

from database import Base, engine
from domain.question.question_router import router as question_router


# 초기 개발 단계에서만 사용하는 테이블 생성 코드.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title='Mars Board API - Week 14',
    description='문제8 질문 등록 기능 - QuestionCreate 스키마 + ORM + Depends',
)


@app.get('/')
def read_root() -> Dict[str, str]:
    return {'message': 'Mars Board API (week_14) is running'}


# 문제8 요구사항: question 라우터 등록
app.include_router(question_router)





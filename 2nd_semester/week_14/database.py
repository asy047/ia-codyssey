from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    contextlib.contextmanager 를 사용해서 데이터베이스 세션을 관리한다.

    with db_session() as db:
        # db 사용
    블록을 벗어나면 자동으로 close() 가 호출된다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의 Depends 에서 사용할 의존성 주입용 함수.

    내부적으로 contextlib 기반 db_session() 을 사용하여
    요청마다 세션을 열고, 응답 후 자동으로 닫아준다.
    """
    with db_session() as db:
        yield db





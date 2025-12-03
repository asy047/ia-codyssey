from typing import Any, Dict, List
from pathlib import Path
import csv

from fastapi import APIRouter, FastAPI, HTTPException


TODO_CSV_FILE = 'todo_list.csv'
todo_list: List[Dict[str, Any]] = []

router = APIRouter(
    prefix='/todo',
    tags=['todo'],
)


def load_todo_list_from_csv() -> None:
    """CSV 파일에서 todo_list 를 읽어온다."""
    todo_list.clear()
    csv_path = Path(TODO_CSV_FILE)

    if not csv_path.exists():
        # 파일이 없으면 아무 것도 하지 않는다.
        return

    with csv_path.open(encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            # CSV의 각 행을 dict 형태로 todo_list 에 추가
            todo_item: Dict[str, Any] = {
                'id': row.get('id', '').strip(),
                'task': row.get('task', '').strip(),
            }
            if todo_item['id'] and todo_item['task']:
                todo_list.append(todo_item)


def append_todo_to_csv(todo_item: Dict[str, Any]) -> None:
    """단일 todo 항목을 CSV 파일에 추가한다."""
    csv_path = Path(TODO_CSV_FILE)
    file_exists = csv_path.exists()

    field_names = ['id', 'task']

    with csv_path.open(mode='a', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'id': todo_item.get('id', ''),
            'task': todo_item.get('task', ''),
        })


def get_next_todo_id() -> int:
    """다음에 사용할 todo id 값을 계산한다."""
    if not todo_list:
        return 1

    max_id = 0
    for item in todo_list:
        try:
            item_id = int(item.get('id', 0))
        except ValueError:
            item_id = 0

        if item_id > max_id:
            max_id = item_id

    return max_id + 1


def is_empty_dict(data: Dict[str, Any]) -> bool:
    """
    Dict 타입이 비어있는지 검사한다.
    - 키가 하나도 없거나
    - 모든 값이 공백 문자열 또는 None 인 경우
    """
    if not data:
        return True

    for value in data.values():
        if value is None:
            continue

        text = str(value).strip()
        if text:
            return False

    return True


@router.post('/add')
async def add_todo(todo: Dict[str, Any]) -> Dict[str, Any]:
    """
    새로운 TODO 항목을 추가한다.
    - 입력: Dict 타입(JSON 객체)
      예: { "task": "FastAPI 공부하기" }
    - 출력: 추가된 todo 정보와 메시지(Dict)
    """
    # 보너스 과제: 입력 Dict 가 비어 있으면 경고 반환
    if is_empty_dict(todo):
        raise HTTPException(
            status_code=400,
            detail='입력된 TODO 데이터가 비어 있습니다.',
        )

    if 'task' not in todo:
        raise HTTPException(
            status_code=400,
            detail='필수 키 "task" 가 누락되었습니다.',
        )

    task_text = str(todo['task']).strip()
    if not task_text:
        raise HTTPException(
            status_code=400,
            detail='할 일 내용("task")이 비어 있습니다.',
        )

    new_id = get_next_todo_id()
    new_todo: Dict[str, Any] = {
        'id': str(new_id),
        'task': task_text,
    }

    todo_list.append(new_todo)
    append_todo_to_csv(new_todo)

    return {
        'message': '새 TODO 항목이 추가되었습니다.',
        'todo': new_todo,
    }


@router.get('/list')
async def retrieve_todo() -> Dict[str, Any]:
    """
    TODO 리스트 전체를 조회한다.
    - 출력: count(개수), items(목록) 을 포함한 Dict
    """
    return {
        'count': len(todo_list),
        'items': todo_list,
    }


app = FastAPI(
    title='Simple TODO API (FastAPI)',
    description='문제1 또 새로운 프로젝트 - FastAPI, CSV 기반 TODO 시스템',
)


@app.on_event('startup')
async def startup_event() -> None:
    """애플리케이션 시작 시 CSV 파일에서 데이터를 읽어온다."""
    load_todo_list_from_csv()


app.include_router(router)

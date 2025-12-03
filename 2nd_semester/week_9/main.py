from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pathlib import Path
import csv

from models import TodoCreate, TodoItem

DATA_FILE = Path('todos.csv')
CSV_FIELDNAMES = ['id', 'title', 'description', 'completed']

app = FastAPI()


def initialize_csv_file() -> None:
    if not DATA_FILE.exists():
        with DATA_FILE.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()


def read_all_todos() -> List[Dict[str, str]]:
    initialize_csv_file()
    todos: List[Dict[str, str]] = []

    with DATA_FILE.open('r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            todos.append(row)

    return todos


def write_all_todos(todos: List[Dict[str, str]]) -> None:
    with DATA_FILE.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for todo in todos:
            writer.writerow(todo)


def get_next_id(todos: List[Dict[str, str]]) -> int:
    if not todos:
        return 1

    max_id = 0
    for todo in todos:
        try:
            todo_id = int(todo['id'])
        except ValueError:
            continue
        if todo_id > max_id:
            max_id = todo_id

    return max_id + 1


def get_todo_by_id(todo_id: int) -> Dict[str, str] | None:
    todos = read_all_todos()
    for todo in todos:
        if todo['id'] == str(todo_id):
            return todo
    return None


@app.get('/todos', response_model=List[Dict[str, str]])
def get_todos() -> List[Dict[str, str]]:
    todos = read_all_todos()
    return todos


@app.post('/todos', response_model=Dict[str, str])
def create_todo(todo: TodoCreate) -> Dict[str, str]:
    todos = read_all_todos()
    new_id = get_next_id(todos)

    new_todo = {
        'id': str(new_id),
        'title': todo.title,
        'description': todo.description,
        'completed': 'true' if todo.completed else 'false',
    }

    todos.append(new_todo)
    write_all_todos(todos)

    return new_todo


@app.get('/todos/{todo_id}', response_model=Dict[str, str])
def get_single_todo(todo_id: int) -> Dict[str, str]:
    todo = get_todo_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    return todo


@app.put('/todos/{todo_id}', response_model=Dict[str, str])
def update_todo(todo_id: int, item: TodoItem) -> Dict[str, str]:
    todos = read_all_todos()
    updated_todo: Dict[str, str] | None = None

    for index, todo in enumerate(todos):
        if todo['id'] == str(todo_id):
            updated_todo = {
                'id': str(todo_id),
                'title': item.title,
                'description': item.description,
                'completed': 'true' if item.completed else 'false',
            }
            todos[index] = updated_todo
            break

    if updated_todo is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    write_all_todos(todos)
    return updated_todo


@app.delete('/todos/{todo_id}')
def delete_single_todo(todo_id: int) -> Dict[str, str]:
    todos = read_all_todos()
    deleted: Dict[str, str] | None = None
    remaining_todos: List[Dict[str, str]] = []

    for todo in todos:
        if todo['id'] == str(todo_id):
            deleted = todo
        else:
            remaining_todos.append(todo)

    if deleted is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    write_all_todos(remaining_todos)

    return {'detail': 'Todo deleted', 'id': deleted['id']}


# 실행 예:
# uvicorn main:app --reload

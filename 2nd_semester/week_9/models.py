from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


class TodoItem(BaseModel):
    title: str
    description: str
    completed: bool

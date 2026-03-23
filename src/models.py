from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class PenaltyLevel(BaseModel):
    days_after_open: int
    max_points: int


class TaskModel(BaseModel):
    """Задача внутри подмодуля. Соответствует серверному TaskImportDto."""

    title: str
    type: Literal["task", "theory"] = "task"
    difficulty: str = "medium"
    max_score: int = Field(default=100, ge=1)
    description: Optional[str] = None
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    contentUrl: Optional[str] = None
    testsUrl: Optional[str] = None
    penalties: Optional[List[PenaltyLevel]] = None


class SubmoduleModel(BaseModel):
    """Подмодуль, содержащий задачи. Соответствует серверному SubmoduleImportDto."""

    title: str
    description: Optional[str] = None
    contentUrl: Optional[str] = None
    tasks: List[TaskModel]


class ModuleModel(BaseModel):
    """Модуль курса. Соответствует серверному ModuleImportDto."""

    title: str
    open_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    submodules: List[SubmoduleModel]


class CourseModel(BaseModel):
    """Финальная модель курса. Соответствует серверному CourseImportDto."""

    title: str
    description: Optional[str] = None
    address_name: Optional[str] = None
    open_date: Optional[str] = None
    close_date: Optional[str] = None
    allowed_users: Optional[List[str]] = None
    allowed_groups: Optional[List[str]] = None
    compilers: Optional[List[str]] = None
    seminars: Optional[List[str]] = None
    modules: List[ModuleModel]

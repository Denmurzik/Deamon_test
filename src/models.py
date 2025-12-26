from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ElementType(str, Enum):
    Task = "Task"
    Theory = "Theory"


class Difficulty(str, Enum):
    Easy = "easy"
    Medium = "medium"
    Hard = "hard"


class TaskModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_name: str = Field(..., alias="task_name")

    type: ElementType = Field(default=ElementType.Task)
    difficulty: Optional[Difficulty] = Field(default=None)
    max_score: Optional[int] = Field(default=None)

    description: str
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None


class SubmoduleModel(BaseModel):
    submodule_name: str
    tasks: List[TaskModel]


class ModuleModel(BaseModel):
    module_name: str
    submodules: List[SubmoduleModel]


class CourseModel(BaseModel):
    course_name: str
    description: Optional[str] = None

    # ИСПРАВЛЕНО: Добавлено поле allowed_users
    # Используем default_factory=list, чтобы по умолчанию был пустой список, а не None
    allowed_users: List[str] = Field(default_factory=list)

    modules: List[ModuleModel]

    @field_validator("modules")
    @classmethod
    def modules_non_empty(cls, v: List[ModuleModel]) -> List[ModuleModel]:
        if not v:
            raise ValueError("Course must contain at least one module")
        return v
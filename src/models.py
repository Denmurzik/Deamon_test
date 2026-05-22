from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class PenaltyLevel(BaseModel):
    days_after_open: int
    max_points: int = Field(..., ge=1)


class TaskModel(BaseModel):
    """
    Задача для module-level content или explicit submodule.tasks[].
    Соответствует серверному TaskImportDto.
    """
    model_config = ConfigDict(populate_by_name=True)

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


class ContentItemModel(BaseModel):
    """
    Элемент module.content[].
    Для explicit submodule содержит вложенный tasks[].
    """
    model_config = ConfigDict(populate_by_name=True)

    type: Literal["submodule", "task", "theory"]
    title: str
    description: Optional[str] = None
    contentUrl: Optional[str] = None
    difficulty: Optional[str] = None
    max_score: Optional[int] = Field(default=None, ge=1)
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    testsUrl: Optional[str] = None
    penalties: Optional[List[PenaltyLevel]] = None
    tasks: Optional[List[TaskModel]] = None


class ModuleModel(BaseModel):
    """
    Модуль курса.
    Соответствует серверному ModuleImportDto.
    """
    model_config = ConfigDict(populate_by_name=True)

    title: str
    open_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    content: List[ContentItemModel]


class CourseModel(BaseModel):
    """
    Финальная модель курса для отправки на сервер.
    Соответствует серверному CourseImportDto.
    """
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: Optional[str] = None
    address_name: Optional[str] = None
    open_date: Optional[str] = None
    close_date: Optional[str] = None
    allowed_users: List[str] = Field(default_factory=list)
    allowed_groups: Optional[List[str]] = None
    # List of emails that should be enrolled as teachers for this course.
    # Backend (ImportController) turns each email into a per-course
    # CourseRole.teacher enrollment. No global UserRole.teacher is assigned —
    # tutor-UI visibility on the frontend is driven by /auth/me's
    # gradableCourseIds array, which is populated from course_enrollments.
    teachers: Optional[List[str]] = None
    compilers: Optional[List[str]] = None
    seminars: Optional[List[str]] = None
    modules: List[ModuleModel]

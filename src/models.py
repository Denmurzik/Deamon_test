from __future__ import annotations
from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class ElementType(str, Enum):
    Task = "task"
    Submodule = "submodule"


class ContentItemModel(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["task", "submodule"]
    title: str
    difficulty: Optional[str] = "medium"
    max_score: Optional[int] = 0
    description: Optional[str] = None
    time_limit: Optional[str] = None
    memory_limit: Optional[str] = None
    content_url: Optional[str] = Field(None, alias="contentUrl")
    tests_url: Optional[str] = Field(None, alias="testsUrl")



class ModuleModel(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    module_name: str = Field(..., alias="module_name")

    content: List[ContentItemModel] = Field(..., alias="submodules")


class CourseModel(BaseModel):

    model_config = ConfigDict(populate_by_name=True)

    course_name: str = Field(..., alias="course_name")
    description: Optional[str] = None
    allowed_users: List[str] = Field(default_factory=list, alias="allowed_users")
    address_name: Optional[str] = None
    modules: List[ModuleModel]
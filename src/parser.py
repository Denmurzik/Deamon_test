from __future__ import annotations
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Any
from .exceptions import MissingFileError, StructureError
from .models import CourseModel, ModuleModel, SubmoduleModel, TaskModel, Difficulty, ElementType


def _read_file_content(zip_path: zipfile.Path, path_str: str) -> str:
    file_obj = zip_path / path_str
    if not file_obj.exists():
        raise MissingFileError(f"{path_str} not found in archive")
    return file_obj.read_text(encoding="utf-8")


def _ensure_int(value, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_from_json(course_root: zipfile.Path, json_data: Dict[str, Any]) -> dict:
    modules_data = json_data.get("modules", [])
    parsed_modules: List[ModuleModel] = []

    for mod in modules_data:
        mod_title = mod.get("title", "Untitled Module")
        content_items = mod.get("content", [])

        elements: List[TaskModel] = []

        for item in content_items:
            item_type_str = item.get("type")

            # Обрабатываем и задачи, и теорию
            if item_type_str in ["task", "submodule"]:

                # Определяем тип: submodule -> Theory, task -> Task
                if item_type_str == "submodule":
                    element_type = ElementType.Theory
                    difficulty = None
                    max_score = 0
                else:
                    element_type = ElementType.Task
                    try:
                        difficulty = Difficulty(item.get("difficulty", "Medium"))
                    except ValueError:
                        difficulty = Difficulty.Medium
                    max_score = _ensure_int(item.get("max_score"), 100)

                task_title = item.get("title", "Untitled")
                content_url = item.get("contentUrl")

                description = ""
                if content_url:
                    try:
                        description = _read_file_content(course_root, content_url)
                    except MissingFileError:
                        description = f"Description file missing: {content_url}"

                task = TaskModel(
                    task_name=task_title,
                    type=element_type,
                    description=description,
                    difficulty=difficulty,
                    max_score=max_score,
                    time_limit=item.get("time_limit"),
                    memory_limit=item.get("memory_limit")
                )
                elements.append(task)

        if elements:
            submodule = SubmoduleModel(
                submodule_name="Materials",
                tasks=elements
            )
            parsed_modules.append(ModuleModel(
                module_name=mod_title,
                submodules=[submodule]
            ))
        else:
            print(f"⚠️ Warning: Module '{mod_title}' skipped (no content found).")

    course = CourseModel(
        course_name=json_data.get("title", "Imported Course"),
        description=json_data.get("description"),
        modules=parsed_modules
    )
    return course.model_dump(by_alias=True)


def parse_course_archive(zip_path: Path) -> dict:
    if not zip_path.exists():
        raise FileNotFoundError(f"Archive not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        root = zipfile.Path(zf)
        top_level_dirs = [x for x in root.iterdir() if
                          x.is_dir() and not x.name.startswith("__") and not x.name.startswith(".")]
        course_root = top_level_dirs[0] if len(top_level_dirs) == 1 else root

        course_json_file = course_root / "course.json"
        if course_json_file.exists():
            print(f"📄 Found course.json in {str(course_root)}...")
            try:
                json_data = json.loads(course_json_file.read_text(encoding="utf-8"))
                return _parse_from_json(course_root, json_data)
            except Exception as e:
                print(f"❌ Failed to parse course.json: {e}")
                raise StructureError(f"Invalid course.json: {e}")

        raise StructureError("Only course.json format is supported in this updated src version.")
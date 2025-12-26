from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
from .exceptions import MissingFileError, StructureError
from .models import CourseModel, ModuleModel, SubmoduleModel, TaskModel, Difficulty, ElementType


def _read_file_content(root_path: Path, path_str: str) -> str:
    """Читает содержимое файла по относительному пути."""
    file_path = root_path / path_str
    if not file_path.exists():
        raise MissingFileError(f"{path_str} not found in {root_path}")
    return file_path.read_text(encoding="utf-8")


def _ensure_int(value, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_from_json(course_root: Path, json_data: Dict[str, Any]) -> dict:
    modules_data = json_data.get("modules", [])
    parsed_modules: List[ModuleModel] = []

    for mod in modules_data:
        mod_title = mod.get("title", "Untitled Module")
        content_items = mod.get("content", [])

        elements: List[TaskModel] = []

        for item in content_items:
            item_type_str = item.get("type")

            if item_type_str in ["task", "submodule"]:
                if item_type_str == "submodule":
                    element_type = ElementType.Theory
                    difficulty = None
                    max_score = 0
                else:
                    element_type = ElementType.Task

                    raw_difficulty = str(item.get("difficulty", "medium")).lower()
                    try:
                        difficulty = Difficulty(raw_difficulty)
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

    # ЛОГИКА ИЗВЛЕЧЕНИЯ ALLOWED_USERS
    # Пробуем snake_case (стандарт Python/SQL) и camelCase (стандарт JS/JSON)
    users_list = json_data.get("allowed_users") or json_data.get("allowedUsers") or []

    # Отладочный принт, чтобы убедиться, что парсер видит поле
    print(f"🔎 DEBUG PARSER: Found allowed_users: {users_list}")

    course = CourseModel(
        course_name=json_data.get("title", "Imported Course"),
        description=json_data.get("description"),
        # Передаем найденный список
        allowed_users=users_list,
        modules=parsed_modules
    )

    # model_dump преобразует объект в dict. Поля со значением None могут исключаться,
    # но так как мы поставили default_factory=list, там будет []
    return course.model_dump(by_alias=True)


def parse_course_archive(path: Path) -> dict:
    """
    Parses a course from a directory structure (unpacked archive).
    Kept the function name compatible with existing imports.
    """
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not path.is_dir():
        raise StructureError(f"Provided path is not a directory: {path}")

    if (path / "course.json").exists():
        course_root = path
    else:
        top_level_dirs = [x for x in path.iterdir() if
                          x.is_dir() and not x.name.startswith(".") and not x.name.startswith("__")]

        if len(top_level_dirs) == 1:
            potential_root = top_level_dirs[0]
            if (potential_root / "course.json").exists():
                course_root = potential_root
            else:
                course_root = path
        else:
            course_root = path

    course_json_file = course_root / "course.json"
    if course_json_file.exists():
        print(f"📄 Found course.json in {str(course_root)}...")
        try:
            json_data = json.loads(course_json_file.read_text(encoding="utf-8"))
            return _parse_from_json(course_root, json_data)
        except Exception as e:
            print(f"❌ Failed to parse course.json: {e}")
            raise StructureError(f"Invalid course.json: {e}")

    raise StructureError(f"course.json not found in {course_root}")
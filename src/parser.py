from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
from .exceptions import MissingFileError, StructureError
from .models import CourseModel, ModuleModel, ContentItemModel


def _read_file_content(root_path: Path, path_str: str) -> str:
    """Читает содержимое файла (например, markdown описание) по пути из JSON."""
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
    """
    Преобразует сырой JSON курса в валидированный словарь для отправки.
    """
    modules_data = json_data.get("modules", [])
    parsed_modules: List[ModuleModel] = []

    for mod in modules_data:
        mod_title = mod.get("title", "Untitled Module")
        raw_content = mod.get("content", [])

        module_elements: List[ContentItemModel] = []

        for item in raw_content:
            item_type = item.get("type")
            if item_type not in ["task", "submodule"]:
                continue

            # Загружаем описание задачи или теорию из внешнего файла
            content_url = item.get("contentUrl")
            description = ""
            if content_url:
                try:
                    description = _read_file_content(course_root, content_url)
                except Exception:
                    description = f"Content missing at: {content_url}"

            # Создаем элемент (задачу или подмодуль)
            element = ContentItemModel(
                type=item_type,
                title=item.get("title", "Untitled"),
                difficulty=str(item.get("difficulty", "medium")).lower(),
                max_score=_ensure_int(
                    item.get("max_score"), 100 if item_type == "task" else 0
                ),
                description=description,
                time_limit=item.get("time_limit"),
                memory_limit=item.get("memory_limit"),
                contentUrl=content_url,
                testsUrl=item.get("testsUrl"),
            )
            module_elements.append(element)

        parsed_modules.append(
            ModuleModel(
                module_name=mod_title,
                open_date=mod.get("open_date"),
                start_date=mod.get("start_date"),
                end_date=mod.get("end_date"),
                penalties=mod.get("penalties"),
                submodules=module_elements,  # Передаем в аргумент с именем алиаса
            )
        )

    # Извлекаем список разрешенных пользователей
    allowed_users = (
        json_data.get("allowed_users") or json_data.get("allowedUsers") or []
    )
    print(f"🔎 DEBUG: Parser found allowed_users: {allowed_users}")

    course = CourseModel(
        course_name=json_data.get("title", "Imported Course"),
        description=json_data.get("description"),
        open_date=json_data.get("open_date"),
        close_date=json_data.get("close_date"),
        allowed_users=allowed_users,
        compilers=json_data.get("compilers"),
        address_name=json_data.get("address_name"),
        modules=parsed_modules,
    )

    # by_alias=True критически важен, чтобы ключи в JSON совпали с ожиданиями сервера
    return course.model_dump(by_alias=True)


def parse_course_archive(path: Path) -> dict:
    """
    Основная точка входа для парсинга папки курса.
    """
    if not path.exists() or not path.is_dir():
        raise StructureError(f"Invalid course path: {path}")

    # Определяем корень курса (где лежит course.json)
    course_root = (
        path if (path / "course.json").exists() else next(path.iterdir(), path)
    )

    course_json_file = course_root / "course.json"
    if not course_json_file.exists():
        raise StructureError(f"course.json not found in {course_root}")

    try:
        json_data = json.loads(course_json_file.read_text(encoding="utf-8"))
        return _parse_from_json(course_root, json_data)
    except Exception as e:
        raise StructureError(f"Failed to parse course.json: {e}")

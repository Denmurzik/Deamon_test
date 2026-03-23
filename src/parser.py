from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .exceptions import MissingFileError, StructureError
from .models import (
    CourseModel, ModuleModel, SubmoduleModel, TaskModel, PenaltyLevel
)


def _read_file_content(root_path: Path, path_str: str) -> str:
    """Читает содержимое файла (например, markdown описание) по пути из JSON."""
    file_path = root_path / path_str
    if not file_path.exists():
        raise MissingFileError(f"{path_str} not found in {root_path}")
    return file_path.read_text(encoding="utf-8")


def _ensure_int(value, default: int, minimum: int = 0) -> int:
    if value is None:
        return default
    try:
        result = int(value)
        return max(result, minimum)
    except (TypeError, ValueError):
        return default


def _parse_penalties(raw: Any) -> Optional[List[PenaltyLevel]]:
    if not raw or not isinstance(raw, list):
        return None
    return [
        PenaltyLevel(
            days_after_open=int(p.get("days_after_open", 0)),
            max_points=max(int(p.get("max_points", 1)), 1),
        )
        for p in raw if isinstance(p, dict)
    ]


def _make_task(item: Dict[str, Any], course_root: Path) -> TaskModel:
    """Создаёт TaskModel из элемента JSON."""
    content_url = item.get("contentUrl")
    description = ""
    if content_url:
        try:
            description = _read_file_content(course_root, content_url)
        except Exception:
            description = f"Content missing at: {content_url}"

    item_type = item.get("type", "task")
    if item_type not in ("task", "theory"):
        item_type = "task"

    return TaskModel(
        title=item.get("title", item.get("task_name", "Untitled")),
        type=item_type,
        difficulty=str(item.get("difficulty", "medium")).lower(),
        max_score=_ensure_int(item.get("max_score"), 100, minimum=1),
        description=description or None,
        time_limit=item.get("time_limit"),
        memory_limit=item.get("memory_limit"),
        contentUrl=content_url,
        testsUrl=item.get("testsUrl"),
        penalties=_parse_penalties(item.get("penalties")),
    )


def _parse_from_json(course_root: Path, json_data: Dict[str, Any]) -> dict:
    """
    Преобразует сырой JSON курса в валидированный словарь для отправки.
    Формат: course.title → modules[].title → submodules[].tasks[]
    """
    modules_data = json_data.get("modules", [])
    parsed_modules: List[ModuleModel] = []

    for mod in modules_data:
        mod_title = mod.get("title", mod.get("module_name", "Untitled Module"))
        raw_content = mod.get("content", mod.get("submodules", []))

        # Группируем элементы в submodules → tasks
        submodules: List[SubmoduleModel] = []
        current_sub_meta: Optional[Dict[str, Any]] = None
        current_tasks: List[TaskModel] = []

        for item in raw_content:
            item_type = item.get("type", "")

            # Уже новый формат: submodule с вложенными tasks[]
            if "tasks" in item and isinstance(item["tasks"], list):
                # Сбросим накопленные задачи
                if current_tasks:
                    _flush_submodule(submodules, current_sub_meta, current_tasks, course_root)
                    current_sub_meta = None
                    current_tasks = []

                sub_content_url = item.get("contentUrl")
                sub_desc = None
                if sub_content_url:
                    try:
                        sub_desc = _read_file_content(course_root, sub_content_url)
                    except Exception:
                        sub_desc = None

                tasks = [_make_task(t, course_root) for t in item["tasks"]]
                submodules.append(SubmoduleModel(
                    title=item.get("title", "Untitled"),
                    description=sub_desc,
                    contentUrl=sub_content_url,
                    tasks=tasks,
                ))
                continue

            # Старый формат: плоский список submodule/task
            if item_type == "submodule":
                if current_tasks or current_sub_meta is not None:
                    _flush_submodule(submodules, current_sub_meta, current_tasks, course_root)
                    current_tasks = []
                current_sub_meta = item

            elif item_type in ("task", "theory"):
                current_tasks.append(_make_task(item, course_root))

        # Финализация оставшихся элементов
        if current_tasks or current_sub_meta is not None:
            _flush_submodule(submodules, current_sub_meta, current_tasks, course_root)

        parsed_modules.append(ModuleModel(
            title=mod_title,
            open_date=mod.get("open_date"),
            start_date=mod.get("start_date"),
            end_date=mod.get("end_date"),
            submodules=submodules,
        ))

    # Извлекаем список разрешенных пользователей
    allowed_users = json_data.get("allowed_users") or json_data.get("allowedUsers") or []
    allowed_groups = json_data.get("allowed_groups") or None
    print(f"🔎 DEBUG: Parser found allowed_users: {allowed_users}")

    course = CourseModel(
        title=json_data.get("title", json_data.get("course_name", "Imported Course")),
        description=json_data.get("description"),
        address_name=json_data.get("address_name"),
        open_date=json_data.get("open_date"),
        close_date=json_data.get("close_date"),
        allowed_users=allowed_users if isinstance(allowed_users, list) else [],
        allowed_groups=allowed_groups if isinstance(allowed_groups, list) else None,
        compilers=json_data.get("compilers"),
        seminars=json_data.get("seminars"),
        modules=parsed_modules,
    )

    return course.model_dump(exclude_none=True)


def _flush_submodule(
    submodules: List[SubmoduleModel],
    meta: Optional[Dict[str, Any]],
    tasks: List[TaskModel],
    course_root: Path,
) -> None:
    """Создаёт SubmoduleModel из мета-данных submodule и накопленных задач."""
    if meta is not None:
        content_url = meta.get("contentUrl")
        description = None
        if content_url:
            try:
                description = _read_file_content(course_root, content_url)
            except Exception:
                description = None
        title = meta.get("title", meta.get("submodule_name", "Untitled"))
    else:
        content_url = None
        description = None
        title = "General"

    submodules.append(SubmoduleModel(
        title=title,
        description=description,
        contentUrl=content_url,
        tasks=tasks,
    ))


def parse_course_archive(path: Path) -> dict:
    """
    Основная точка входа для парсинга папки курса.
    """
    if not path.exists() or not path.is_dir():
        raise StructureError(f"Invalid course path: {path}")

    # Определяем корень курса (где лежит course.json)
    course_root = path if (path / "course.json").exists() else next(path.iterdir(), path)

    course_json_file = course_root / "course.json"
    if not course_json_file.exists():
        raise StructureError(f"course.json not found in {course_root}")

    try:
        json_data = json.loads(course_json_file.read_text(encoding="utf-8"))
        return _parse_from_json(course_root, json_data)
    except StructureError:
        raise
    except Exception as e:
        raise StructureError(f"Failed to parse course.json: {e}")

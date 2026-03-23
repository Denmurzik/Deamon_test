from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any
from .exceptions import MissingFileError, StructureError
from .models import CourseModel, ModuleModel, SubmoduleModel, TaskModel, PenaltyLevel


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


def _parse_penalties(raw: Any) -> List[PenaltyLevel] | None:
    if not raw or not isinstance(raw, list):
        return None
    return [
        PenaltyLevel(
            days_after_open=int(p.get("days_after_open", 0)),
            max_points=max(int(p.get("max_points", 1)), 1),
        )
        for p in raw
        if isinstance(p, dict)
    ]


def _parse_from_json(course_root: Path, json_data: Dict[str, Any]) -> dict:
    """
    Преобразует сырой JSON курса в валидированный словарь для отправки.
    Формат соответствует серверному CourseImportDto:
      course.title → modules[].title → submodules[].title → tasks[]
    """
    modules_data = json_data.get("modules", [])
    parsed_modules: List[ModuleModel] = []

    for mod in modules_data:
        mod_title = mod.get("title", mod.get("module_name", "Untitled Module"))
        raw_content = mod.get("content", mod.get("submodules", []))

        # Группируем элементы: submodule содержит tasks[]
        submodules: List[SubmoduleModel] = []
        current_submodule_tasks: List[TaskModel] = []
        current_submodule_meta: Dict[str, Any] | None = None

        for item in raw_content:
            item_type = item.get("type", "")

            if item_type == "submodule":
                # Если были накопленные задачи без submodule — сохраним в "General"
                if current_submodule_tasks and current_submodule_meta is None:
                    submodules.append(
                        SubmoduleModel(
                            title="General",
                            tasks=current_submodule_tasks,
                        )
                    )
                    current_submodule_tasks = []
                elif current_submodule_meta is not None:
                    # Сохраняем предыдущий submodule
                    _flush_submodule(
                        submodules, current_submodule_meta,
                        current_submodule_tasks, course_root,
                    )
                    current_submodule_tasks = []

                current_submodule_meta = item

            elif item_type in ("task", "theory"):
                content_url = item.get("contentUrl")
                description = ""
                if content_url:
                    try:
                        description = _read_file_content(course_root, content_url)
                    except Exception:
                        description = f"Content missing at: {content_url}"

                task = TaskModel(
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
                current_submodule_tasks.append(task)

            # Если элемент уже в формате submodules[].tasks[] (новый формат)
            elif "tasks" in item:
                sub_content_url = item.get("contentUrl")
                sub_desc = ""
                if sub_content_url:
                    try:
                        sub_desc = _read_file_content(course_root, sub_content_url)
                    except Exception:
                        sub_desc = ""

                tasks = []
                for t in item.get("tasks", []):
                    t_content_url = t.get("contentUrl")
                    t_desc = ""
                    if t_content_url:
                        try:
                            t_desc = _read_file_content(course_root, t_content_url)
                        except Exception:
                            t_desc = f"Content missing at: {t_content_url}"

                    tasks.append(TaskModel(
                        title=t.get("title", "Untitled"),
                        type=t.get("type", "task"),
                        difficulty=str(t.get("difficulty", "medium")).lower(),
                        max_score=_ensure_int(t.get("max_score"), 100, minimum=1),
                        description=t_desc or None,
                        time_limit=t.get("time_limit"),
                        memory_limit=t.get("memory_limit"),
                        contentUrl=t_content_url,
                        testsUrl=t.get("testsUrl"),
                        penalties=_parse_penalties(t.get("penalties")),
                    ))

                submodules.append(SubmoduleModel(
                    title=item.get("title", "Untitled"),
                    description=sub_desc or None,
                    contentUrl=sub_content_url,
                    tasks=tasks,
                ))

        # Финализация последнего submodule / оставшихся задач
        if current_submodule_meta is not None:
            _flush_submodule(
                submodules, current_submodule_meta,
                current_submodule_tasks, course_root,
            )
        elif current_submodule_tasks:
            submodules.append(
                SubmoduleModel(title="General", tasks=current_submodule_tasks)
            )

        parsed_modules.append(
            ModuleModel(
                title=mod_title,
                open_date=mod.get("open_date"),
                start_date=mod.get("start_date"),
                end_date=mod.get("end_date"),
                submodules=submodules,
            )
        )

    allowed_users = (
        json_data.get("allowed_users") or json_data.get("allowedUsers") or None
    )
    allowed_groups = json_data.get("allowed_groups") or None

    course = CourseModel(
        title=json_data.get("title", json_data.get("course_name", "Imported Course")),
        description=json_data.get("description"),
        address_name=json_data.get("address_name"),
        open_date=json_data.get("open_date"),
        close_date=json_data.get("close_date"),
        allowed_users=allowed_users if isinstance(allowed_users, list) else None,
        allowed_groups=allowed_groups if isinstance(allowed_groups, list) else None,
        compilers=json_data.get("compilers"),
        seminars=json_data.get("seminars"),
        modules=parsed_modules,
    )

    return course.model_dump(exclude_none=True)


def _flush_submodule(
    submodules: List[SubmoduleModel],
    meta: Dict[str, Any],
    tasks: List[TaskModel],
    course_root: Path,
) -> None:
    """Создаёт SubmoduleModel из мета-данных и накопленных задач."""
    content_url = meta.get("contentUrl")
    description = ""
    if content_url:
        try:
            description = _read_file_content(course_root, content_url)
        except Exception:
            description = ""

    submodules.append(
        SubmoduleModel(
            title=meta.get("title", meta.get("submodule_name", "Untitled")),
            description=description or None,
            contentUrl=content_url,
            tasks=tasks,
        )
    )


def parse_course_archive(path: Path) -> dict:
    """
    Основная точка входа для парсинга папки курса.
    """
    if not path.exists() or not path.is_dir():
        raise StructureError(f"Invalid course path: {path}")

    course_root = (
        path if (path / "course.json").exists() else next(path.iterdir(), path)
    )

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

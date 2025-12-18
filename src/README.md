Parser for course ZIP archives

Usage:

1. Create a ZIP archive where the top-level folder is the course name. Inside it:
   - Level 1: modules (folders)
   - Level 2: submodules (folders)
   - Level 3: tasks (folders)

Each task folder must contain `statement.md` and either `meta.json` or `meta.yaml` with fields: difficulty, max_score, time_limit, memory_limit.

Run:

python -m parser.runner path/to/course.zip

The `parse_course_archive` function returns a JSON-serializable dict validated by Pydantic models.


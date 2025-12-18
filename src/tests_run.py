from pathlib import Path
import sys

# Ensure project root (Deamon_github) is on sys.path so we can import package `src`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.parser import parse_course_archive
import json

if __name__ == '__main__':
    zip_path = Path(__file__).resolve().parent / 'sample_course.zip'
    res = parse_course_archive(zip_path)
    print(json.dumps(res, ensure_ascii=False, indent=2))

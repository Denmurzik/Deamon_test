"""Parser package for converting course ZIP archives into JSON suitable for LMS import."""

from .parser import parse_course_archive
from .client import CourseUploader
from .models import CourseModel

__all__ = ["parse_course_archive", "CourseUploader", "CourseModel"]
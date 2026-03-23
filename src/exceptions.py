from pathlib import Path


class ParserError(Exception):
    """Base class for src-related errors."""


class StructureError(ParserError):
    """Raised when the archive structure does not follow expected hierarchy."""


class MissingFileError(ParserError):
    """Raised when a required file is missing."""

    def __init__(self, path: Path | str, message: str | None = None) -> None:
        if message is None:
            message = f"Missing required file: {path}"
        super().__init__(message)
        self.path = str(path)


class APIClientError(ParserError):
    """Raised when interaction with the LMS API fails."""
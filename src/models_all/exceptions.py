from fastapi import HTTPException


class AppException(HTTPException):
    """Base for all application-raised HTTPExceptions."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class GenericException(AppException):
    """Raised when an unexpected error occurs."""

    def __init__(
        self,
        detail: str = "An unexpected error occurred. Please try again later.",
    ):
        super().__init__(status_code=500, detail=detail)


class DatabaseConnectionError(AppException):
    """Raised when could not connect to the database."""

    def __init__(
        self,
        detail: str = "Could not connect to the database. Please try again later.",
    ):
        super().__init__(status_code=500, detail=detail)


class NotFoundException(AppException):
    """Raised when a resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenException(AppException):
    """Raised when the user does not have permission."""

    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=403, detail=detail)


class UnauthorizedException(AppException):
    """Raised when authentication fails or is missing."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class BadRequestException(AppException):
    """Raised when the request is invalid."""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


# --- Telegram Specific Exceptions ---

class TelegramRateLimitError(AppException):
    """Raised when Telegram returns a 429 Too Many Requests response."""

    def __init__(self, retry_after: int, message: str = "Rate limited by Telegram"):
        self.retry_after = retry_after
        super().__init__(status_code=429, detail=f"{message} (retry_after={retry_after}s)")


class TelegramAPIError(AppException):
    """Raised when Telegram returns a non-2xx, non-429 response."""

    def __init__(self, status_code: int, description: str):
        self.status_code = status_code
        self.description = description
        super().__init__(status_code=status_code, detail=f"Telegram API error {status_code}: {description}")

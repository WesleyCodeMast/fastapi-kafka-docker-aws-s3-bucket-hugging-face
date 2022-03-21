from fastapi import HTTPException


class APIError(HTTPException):
    status_code: int
    field: str = None
    detail: str = None
    code: str = None

    def __init__(self, field: str = None, detail: str = None, **kwargs) -> None:
        if field is not None:
            self.field = field

        if detail is not None:
            self.detail = detail

        if self.field and self.detail:
            detail = {self.field: self.detail}
        else:
            detail = self.detail

        super().__init__(detail=detail, status_code=self.status_code, **kwargs)


__all__ = (
    'APIError',
)

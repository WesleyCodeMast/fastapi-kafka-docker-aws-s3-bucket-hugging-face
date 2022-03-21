from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import validation_error_response_definition

from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from pydantic import ValidationError

from core.schemas import Error, ErrorWrapper

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.exceptions import APIError


def http_exception_handler(_: Request, exception: HTTPException) -> JSONResponse:
    serializer = ErrorWrapper()

    if isinstance(exception.detail, dict):
        serializer.errors = [Error(field=field, detail=detail) for field, detail in exception.detail.items()]
    else:
        serializer.errors = [Error(detail=exception.detail, code=str(exception.status_code))]

    return JSONResponse(serializer.model_dump(exclude_none=True), status_code=exception.status_code)


def request_validation_exception_handler(
    _: 'Request',
    exception: RequestValidationError | ValidationError,
) -> JSONResponse:
    return JSONResponse({'errors': exception.errors()}, status_code=HTTP_422_UNPROCESSABLE_ENTITY)


def api_error_handler(_: Request, exception: 'APIError') -> JSONResponse:
    serializer = ErrorWrapper()

    if isinstance(exception.detail, dict):
        serializer.errors = [
            Error(field=field, detail=detail, code=exception.code) for field, detail in exception.detail.items()
        ]
    else:
        serializer.errors = [Error(
            detail=exception.detail,
            code=exception.code,
            field=exception.field,
        )]

    return JSONResponse(serializer.model_dump(exclude_none=True), status_code=exception.status_code)


validation_error_response_definition['properties'] = {
    'errors': {
        'title': 'Errors',
        'type': 'array',
        'items': {'$ref': '{0}ValidationError'.format(REF_PREFIX)},
    },
}


__all__ = (
    'request_validation_exception_handler',
    'http_exception_handler',
    'api_error_handler',
)

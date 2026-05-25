from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def _build_error_response(message, errors=None, error_code='ERROR', status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            'success': False,
            'message': message,
            'errors': errors or {},
            'error_code': error_code,
            'timestamp': timezone.now().isoformat(),
        },
        status=status_code,
    )


def custom_exception_handler(exc, context):
    """Return consistent API error envelopes for DRF exceptions."""
    response = drf_exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        detail = exc.detail
        if isinstance(detail, list):
            errors = {'non_field_errors': [str(item) for item in detail]}
        elif isinstance(detail, dict):
            errors = {
                key: [str(item) for item in value] if isinstance(value, list) else [str(value)]
                for key, value in detail.items()
            }
        else:
            errors = {'non_field_errors': [str(detail)]}
        return _build_error_response(
            message='Validation Error',
            errors=errors,
            error_code='VALIDATION_ERROR',
            status_code=response.status_code if response else status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            errors = {
                key: [str(item) for item in value] if isinstance(value, list) else [str(value)]
                for key, value in exc.message_dict.items()
            }
        elif hasattr(exc, 'messages'):
            errors = {'non_field_errors': [str(item) for item in exc.messages]}
        else:
            errors = {'non_field_errors': [str(exc)]}
        return _build_error_response(
            message='Validation Error',
            errors=errors,
            error_code='VALIDATION_ERROR',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, (NotFound, Http404)):
        return _build_error_response(
            message='Resource not found',
            errors={'detail': ['The requested resource was not found.']},
            error_code='NOT_FOUND',
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, PermissionDenied):
        return _build_error_response(
            message='Permission denied',
            errors={'detail': [str(exc.detail) if hasattr(exc, 'detail') else 'Permission denied.']},
            error_code='PERMISSION_DENIED',
            status_code=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return _build_error_response(
            message='Authentication failed',
            errors={'detail': [str(exc.detail) if hasattr(exc, 'detail') else 'Authentication required.']},
            error_code='AUTHENTICATION_FAILED',
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, Throttled):
        return _build_error_response(
            message='Request throttled',
            errors={'detail': [f'Request was throttled. Retry after {exc.wait} seconds.']},
            error_code='THROTTLED',
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if response is None:
        return _build_error_response(
            message='Server Error',
            errors={'detail': ['An unexpected error occurred.']},
            error_code='SERVER_ERROR',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if response.status_code >= 500:
        return _build_error_response(
            message='Server Error',
            errors={'detail': [str(exc)]},
            error_code='SERVER_ERROR',
            status_code=response.status_code,
        )

    detail = getattr(exc, 'detail', str(exc))
    if isinstance(detail, dict):
        errors = detail
        message = 'Request failed'
    else:
        errors = {'detail': [str(detail)]}
        message = str(detail)
    return _build_error_response(
        message=message,
        errors=errors,
        error_code='ERROR',
        status_code=response.status_code,
    )

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)

def api_exception_handler(exc, context):
    """
    Custom exception handler that mimics the Regular 'errorConverter' and 'errorHandler'.
    Returns a consistent JSON structure: { "code": 400, "message": "Error details", "stack": ... }
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Handle Django Validation Errors (which DRF doesn't handle by default)
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            # Convert {field: [errors]} to string
            msg = "; ".join([f"{k}: {v[0]}" for k, v in exc.message_dict.items()])
        elif hasattr(exc, 'messages'):
             msg = ", ".join(exc.messages)
        else:
            msg = str(exc)
        return Response({'code': status.HTTP_400_BAD_REQUEST, 'message': msg}, status=status.HTTP_400_BAD_REQUEST)

    # If response is None, it means there's an unhandled exception (Internal Server Error)
    if response is None:
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        return Response(
            {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Internal Server Error',
                # Stack trace would go here in DEV mode if needed, similar to Regular
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Standardize DRF responses
    # DRF usually returns {"detail": "..."} or {"field": ["..."]}
    error_message = ""
    if isinstance(response.data, dict):
        if 'detail' in response.data:
            error_message = response.data['detail']
        else:
            # Join field errors: "email: Invalid email, password: required"
            error_message = ", ".join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in response.data.items()])
    elif isinstance(response.data, list):
        error_message = ", ".join(response.data)
    else:
        error_message = str(response.data)

    # Override the data with our custom format
    response.data = {
        'code': response.status_code,
        'message': error_message
    }

    return response
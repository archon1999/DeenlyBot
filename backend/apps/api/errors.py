from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        return Response(
            exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages},
            status=400,
        )
    if isinstance(exc, ObjectDoesNotExist):
        return Response({"detail": "Not found."}, status=404)
    if isinstance(exc, ValueError):
        return Response({"detail": str(exc)}, status=400)
    return drf_exception_handler(exc, context)

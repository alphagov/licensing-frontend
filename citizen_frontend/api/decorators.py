import logging
from collections.abc import Callable

from django.http.response import JsonResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handle_exceptions(func: Callable):
    def interceptor(request, **kwargs):
        try:
            return func(request, **kwargs)
        except Exception as e:
            logger.exception("Unhandled exception: %s", str(e))
            return JsonResponse(
                status=500,
                data={"message": f"Unhandled exception: {str(e)}"},
                safe=False,
            )

    return interceptor

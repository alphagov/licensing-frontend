import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from pydantic import ValidationError

import citizen_frontend.api.repository.licence_repository as licence_repository
import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.api.decorators import handle_exceptions
from citizen_frontend.api.models.api_responses import LicenceResponse
from citizen_frontend.exceptions import DataError, DocumentDBError, LicenceLookupError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@require_GET
@handle_exceptions
def get_all_licences(request):
    try:
        logger.info("Fetching all licences")
        licences = licence_repository.get_all_licences()

        if not licences:
            return JsonResponse(status=404, data="No licences found", safe=False)

        response = [
            LicenceResponse(
                name=licence.name, code=licence.licence_code, legislation=licence.legislation_name
            ).model_dump()
            for licence in licences
        ]
        return JsonResponse(response, safe=False)
    except ValidationError as e:
        logger.error(e)
        return JsonResponse(status=404, data="Invalid response", safe=False)
    except (DataError, DocumentDBError) as e:
        return JsonResponse(status=404, data=e.args, safe=False)


@require_GET
@handle_exceptions
def get_licence_authorities_and_interactions(request, licence_code: str, snac_code: str | None = None):
    try:
        result = licence_lookup_service.get_licence_authorities_and_interactions(
            licence_code=licence_code, snac_code=snac_code
        )

        response = result.model_dump(by_alias=True, exclude_none=True)

        return JsonResponse(status=200, data=response, safe=False)
    except LicenceLookupError as e:
        return JsonResponse(status=404, data=e.args[0], safe=False)

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.api.models.api_responses import LicenceResponse
from citizen_frontend.api.utils import get_all_licences_from_database


@require_GET
def get_all_licences(request):
    try:
        licences = get_all_licences_from_database()

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
        return JsonResponse(status=404, data=e.messages, safe=False)


@require_GET
def get_licence_authorities_and_interactions(request, licence_code: str, snac_code: str | None = None):
    result = licence_lookup_service.get_licence_authorities_and_interactions(
        licence_code=licence_code, snac_code=snac_code
    )

    if not result:
        return JsonResponse(status=404, data="No licences found", safe=False)

    response = result.model_dump(by_alias=True, exclude_none=True)

    return JsonResponse(status=200, data=response, safe=False)

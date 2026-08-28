from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from citizen_frontend.api.models.api_responses import LicenceResponse
from citizen_frontend.api.services.licence_lookup_service import LicenceLookupService
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
        # is this how we would like to handle this type of error?
        # if using pydantic we need to handle these pydantic e too
        #  maybe 500ish response
        return JsonResponse(status=404, data=e.messages, safe=False)


@require_GET
def get_licence_authority_and_interactions_by_licence_code(request, licence_code):
    licence_lookup_service = LicenceLookupService()
    licence_authorities_and_interactions = licence_lookup_service.get_licence_authority_and_interactions(
        licence_code=licence_code
    )

    if not licence_authorities_and_interactions:
        return JsonResponse(status=404, data="No licences found", safe=False)

    response = licence_authorities_and_interactions.model_dump(by_alias=True, exclude_none=True)

    return JsonResponse(status=200, data=response, safe=False)


@require_GET
def get_licence_authorities_and_interactions_by_licence_code_and_snac_code(request, licence_code: str, snac_code: str):
    licence_lookup_service = LicenceLookupService()
    result = licence_lookup_service.licence_authorities_and_interactions_by_snac_code(
        snac_code=snac_code, licence_code=licence_code
    )

    if not result:
        return JsonResponse(status=404, data="No licences found", safe=False)

    response = result.model_dump(by_alias=True, exclude_none=True)

    return JsonResponse(status=200, data=response, safe=False)

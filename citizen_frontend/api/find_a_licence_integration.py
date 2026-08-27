from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

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
        # is this how we would like to handle this type of error?
        # if using pydantic we need to handle these pydantic e too
        #  maybe 500ish response
        return JsonResponse(status=404, data=e.messages, safe=False)


def get_licence_authority_and_interactions_by_licence_code(request, licence_code):
    return JsonResponse(status=200, data={"body": "hello"})

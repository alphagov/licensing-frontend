from django.core.exceptions import ValidationError
from django.http import JsonResponse

from citizen_frontend.api.models.api_responses import LicenceResponse
from citizen_frontend.api.utils import get_all_licences_from_database


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
        #  maybe 500 error
        return JsonResponse(status=404, data=e.messages, safe=False)

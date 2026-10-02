from common.models.licences import Licence


def get_licence_by_licence_code(licence_code: str) -> Licence | None:
    try:
        licences = list(Licence.objects.filter(licence_code=licence_code))
        if licences:
            for licence in licences:
                licence.full_clean()
            return licences[0]
    except Licence.DoesNotExist:
        return None

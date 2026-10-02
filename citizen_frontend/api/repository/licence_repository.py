from common.models.licences import Licence


def get_licence_by_licence_code(licence_code: str) -> Licence | None:
    try:
        licence = Licence.objects.get(licence_code=licence_code)
        if licence:
            return licence
    except Licence.DoesNotExist:
        return None

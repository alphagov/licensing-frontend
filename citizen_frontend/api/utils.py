from common.models.licences import Licence


def get_all_licences_from_database() -> list[Licence]:
    licences = Licence.objects.all()
    return list(licences)

from django.http import Http404


def get_mocked_context(licence, authority, interaction, interation_sub_id):
    if authority != "winchester":
        raise Http404

    if licence not in ["temporary-event-notice", "food-premises-approval-6"]:
        raise Http404

    supporting_documents = [
        {"name": "Scale plan of establishment", "is_mandatory": True},
        {"name": "Information required by section 9 of the form", "is_mandatory": True},
        {"name": "Additional information for section 9 of the form", "is_mandatory": False},
    ]

    fee = get_fee(licence)
    steps = 4 if fee else 3

    context = {
        "authority": authority.capitalize(),
        "licence": licence.replace("-", " ").title(),
        "fee": fee,
        "steps": steps,
        "supporting_documents": None if licence == "temporary-event-notice" else supporting_documents,
    }

    return context


def get_fee(licence: str):
    if licence == "temporary-event-notice":
        return pence_to_pounds(2100)
    elif licence == "food-premises-approval-6":
        return None
    return None


def pence_to_pounds(pence: int) -> str:
    pounds = int(pence / 100)
    return f"£{pounds}.00"

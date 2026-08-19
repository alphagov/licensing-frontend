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

    temp_event_declarations = [
        "The information contained in this form is correct to the best of my knowledge and belief",
        "I understand that it is an offence:",
        "(i) to knowingly or recklessly make a false statement in connection with this "
        "temporary event notice and that a person is liable on conviction for such an offence to "
        "a fine up to level 5 on the standard scale; and",
        "(ii) to permit an unauthorised licensable activity to be carried on at "
        "any place and that a person is liable on conviction for any such offence to a fine not exceeding £20,000,"
        " or to imprisonment for a term not exceeding six months, or to both",
    ]
    food_premises_declarations = [
        "I hereby apply, as food business operator of the establishment detailed in Part 1, "
        "for approval to use that establishment for the purposes of "
        "handling products of animal origin "
        "for which Regulation (EC) No. 853/2004 lays down requirements, "
        "as set out in the relevant Parts of this document."
    ]

    fee = get_fee(licence)
    steps = 4 if fee else 3

    context = {
        "authority": authority.capitalize(),
        "licence": licence.replace("-", " ").title(),
        "interation_sub_id": interation_sub_id,
        "interaction": interaction,
        "fee_required": fee[0],
        "fee": fee[1],
        "steps": steps,
        "authority_slug": authority,
        "licence_slug": licence,
        "supporting_documents": None if licence == "temporary-event-notice" else supporting_documents,
        "default_declarations": (
            temp_event_declarations if licence == "temporary-event-notice" else food_premises_declarations
        ),
    }

    return context


def get_fee(licence: str):
    if licence == "temporary-event-notice":
        return True, pence_to_pounds(2100)
    elif licence == "food-premises-approval-6":
        return False, None
    return None


def pence_to_pounds(pence: int) -> str:
    pounds = int(pence / 100)
    return f"£{pounds}.00"

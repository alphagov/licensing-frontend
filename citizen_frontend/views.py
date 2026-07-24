from django.shortcuts import render


def index(request, licence, authority, interaction, interation_sub_id):
    supporting_documents = [
        {"name": "Scale plan of establishment", "is_mandatory": True},
        {"name": "Information required by section 9 of the form", "is_mandatory": True},
        {"name": "Additional information for section 9 of the form", "is_mandatory": False},
    ]
    fee = 2100 if licence == "temporary-event-notice" else None
    steps = 4 if fee else 3
    context = {
        "authority": authority.capitalize(),
        "licence": licence.replace("-", " ").title(),
        "fee": pence_to_pounds(fee) if fee else None,
        "steps": steps,
        "supporting_documents": None if licence == "temporary-event-notice" else supporting_documents,
    }

    return render(request, "citizen_frontend/licence_introduction_page.html", context)


def pence_to_pounds(pence: int) -> str:
    pounds = int(pence / 100)
    return f"£{pounds}.00"

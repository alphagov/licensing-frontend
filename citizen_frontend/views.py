from django.shortcuts import render


def index(request, licence, authority, interaction, interation_sub_id):
    fee = 2100 if licence == "temporary-event-notice" else None
    steps = 4 if fee else 3
    context = {
        "authority": authority.capitalize(),
        "licence": licence.replace("-", " ").title(),
        "fee": pence_to_pounds(fee) if fee else None,
        "steps": steps,
    }

    return render(request, "citizen_frontend/licence_introduction_page.html", context)


def pence_to_pounds(pence: int) -> str:
    pounds = int(pence / 100)
    return f"£{pounds}.00"

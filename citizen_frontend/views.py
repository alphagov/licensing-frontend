from django.shortcuts import render


def index(request, licence, authority, interaction, interation_sub_id):

    context = {
        "authority": authority.capitalize(),
        "licence": licence.replace("-", " ").title(),
    }

    return render(request, "citizen_frontend/licence_introduction_page.html", context)

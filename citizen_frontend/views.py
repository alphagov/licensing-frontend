from django.http import Http404
from django.shortcuts import render

from citizen_frontend.forms.licence_submission import ApplicationSubmissionForm
from citizen_frontend.mocks import get_mocked_context


def index(request, licence, authority, interaction, interation_sub_id):
    try:
        context = get_mocked_context(licence, authority, interaction, interation_sub_id)
        context.update({"step": 1})
        return render(request, "citizen_frontend/licence_introduction_page.html", context)
    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e


def submit_form(request, licence, authority, interaction, interation_sub_id):
    try:
        context = get_mocked_context(licence, authority, interaction, interation_sub_id)
        context.update({"step": 2})
        form = ApplicationSubmissionForm(context=context)
        context.update({"form": form})

        return render(request, "citizen_frontend/licence_submission_page.html", context)

    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e

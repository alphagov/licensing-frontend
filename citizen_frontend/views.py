from django.http import Http404
from django.http.response import HttpResponse
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

        if request.method == "POST":
            form = ApplicationSubmissionForm(
                request.POST,
                fee=context.get("fee_amount"),
                supporting_documents=context.get("supporting_documents"),
                default_declarations=context.get("default_declarations"),
            )

            if form.is_valid():
                pass

        else:
            form = ApplicationSubmissionForm(
                fee=context.get("fee_amount"),
                supporting_documents=context.get("supporting_documents"),
                default_declarations=context.get("default_declarations"),
            )

        context.update({"form": form})

        return render(request, "citizen_frontend/licence_submission_page.html", context)

    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e


def get_all_licences(request):
    get_all_licences_from_db()
    return HttpResponse()


def get_all_licences_from_db():
    pass

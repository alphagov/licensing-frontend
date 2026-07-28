from crispy_forms.layout import HTML
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Fieldset, Layout
from django import forms
from django.core.validators import FileExtensionValidator
from django.template.loader import render_to_string


class ApplicationSubmissionForm(forms.Form):
    email = forms.EmailField(
        help_text="Please provide your email address, "
        "so the licensing authority can let you know if your application has been successful or not.",
        error_messages={
            "required": "Please provide your email address",
            "invalid": "Enter an email address in the correct format, like name@example.com",
        },
        widget=forms.TextInput(attrs={"data-testid": "email-field"}),
        label="Email address",
    )

    confirmation_email = forms.EmailField(
        label="Confirmation email address",
        error_messages={
            "required": "Please confirm your email address",
            "invalid": "Enter an email address in the correct format, like name@example.com",
        },
        widget=forms.TextInput(attrs={"data-testid": "confirmation-email-field"}),
    )

    application_upload = forms.FileField(
        help_text="Please attach the completed application form below.",
        error_messages={"required": "Please provide filled Application form in PDF format"},
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        label="Application Form",
        widget=forms.FileInput(attrs={"data-testid": "application-upload", "class": "govuk-file-upload"}),
    )

    def __init__(self, context):
        super().__init__()
        layout_items = [
            Fieldset("email", "confirmation_email", legend="Email address", legend_tag="h2", legend_size="s"),
            Fieldset("application_upload", accept=".pdf", legend="Application form", legend_tag="h2", legend_size="s"),
        ]

        if context.get("supporting_documents"):
            layout_items.append(self.render_supporting_documents(context))

        self.helper = FormHelper()
        self.helper.layout = Layout(*layout_items)

    def render_supporting_documents(self, context):
        fieldset_additions = [
            HTML(
                render_to_string(
                    "citizen_frontend/partials/supporting_documents_upload_additional_information.html", context=context
                )
            ),
        ]

        supporting_documents = context["supporting_documents"]

        for index, document in enumerate(supporting_documents):
            self.fields[f"supporting_document_{index}"] = forms.FileField(
                label=document["name"],
                help_text=document.get("description", "add description to test models"),
                required=document["is_mandatory"],
                widget=forms.FileInput(
                    attrs={"data-testid": f"supporting-document-upload-{index}", "class": "govuk-file-upload"}
                ),
            )

            fieldset_additions.append(f"supporting_document_{index}")

        return Fieldset(*fieldset_additions, legend="Supporting Documents", legend_tag="h2", legend_size="s")

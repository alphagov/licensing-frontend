from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Fieldset, Layout
from django import forms
from django.core.validators import FileExtensionValidator


class SubmissionEmailForm(forms.Form):
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
        self.context = context
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset("email", "confirmation_email", legend="Email address", legend_tag="h2", legend_size="s"),
            Fieldset("application_upload", accept=".pdf", legend="Application form", legend_tag="h2", legend_size="s"),
        )

    # def render_supporting_documents(self):
    #     for index, supporting_document in enumerate(self.context.supporting_documents):
    #         supporting_document_upload = forms.FileField(
    #             label=
    #         )

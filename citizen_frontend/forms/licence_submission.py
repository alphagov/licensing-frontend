from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import HTML, Button, Fieldset, Layout
from django import forms
from django.core.validators import FileExtensionValidator
from django.template.loader import render_to_string


class ApplicationSubmissionForm(forms.Form):
    email = forms.EmailField(
        help_text="Please provide your email address, "
        "so the licensing authority can let you know if your application has been successful or not.",
        # error_messages={
        #     "required": "Please provide your email address",
        #     "invalid": "Enter an email address in the correct format, like name@example.com",
        # },
        error_messages={"required": "Enter your name as it appears on your passport"},
        widget=forms.TextInput(attrs={"data-testid": "email-field", "autocomplete": "email"}),
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
        widget=forms.FileInput(
            attrs={
                "data-testid": "application-upload",
                "class": "govuk-file-upload",
            }
        ),
    )

    def __init__(self, *args, supporting_documents, default_declarations, fee, **kwargs):
        super().__init__(*args, **kwargs)

        layout_items = [
            Fieldset("email", "confirmation_email", legend="Email address", legend_tag="h2", legend_size="s"),
            Fieldset("application_upload", accept=".pdf", legend="Application form", legend_tag="h2", legend_size="s"),
        ]

        if supporting_documents:
            (
                layout_items.append(
                    self.build_supporting_documents_fieldset({"supporting_documents": supporting_documents})
                )
            )

        if default_declarations:
            layout_items.append(self.build_declarations_fieldset({"default_declarations": default_declarations}))

        layout_items.append(HTML(render_to_string("citizen_frontend/partials/submission_statement.html")))

        submit_button_text = "Continue to pay fee" if fee else "Submit Application"

        layout_items.append(
            Button.primary(
                "submit",
                submit_button_text,
                data_testid="submit-button",
            )
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(*layout_items)

    def build_supporting_documents_fieldset(self, context):
        fieldset_additions = [
            HTML(
                render_to_string(
                    "citizen_frontend/partials/supporting_documents_upload_additional_information.html", context=context
                )
            ),
        ]

        supporting_documents = context["supporting_documents"]

        for index, document in enumerate(supporting_documents):
            label = document["name"] if document["is_mandatory"] else f"{document['name']}(optional)"

            self.fields[f"supporting_document_{index}"] = forms.FileField(
                label=label,
                help_text=document.get("description", "add description to test models"),
                required=document["is_mandatory"],
                widget=forms.FileInput(
                    attrs={"data-testid": f"supporting-document-upload-{index}", "class": "govuk-file-upload"}
                ),
                validators=[
                    FileExtensionValidator(
                        allowed_extensions=[
                            "pdf",
                            "docx",
                            "doc",
                            "gif",
                            "jpp",
                            "jpeg",
                            "png",
                            "ppt",
                            "pptx",
                            "rtf",
                            "txt",
                            "xls",
                            "xlsx",
                        ]
                    )
                ],
            )

            fieldset_additions.append(f"supporting_document_{index}")

        return Fieldset(*fieldset_additions, legend="Supporting Documents", legend_tag="h2", legend_size="s")

    def build_declarations_fieldset(self, context):
        fieldset_additions = [HTML(render_to_string("citizen_frontend/partials/declarations.html", context=context))]

        self.fields["declaration"] = forms.BooleanField(
            label="Ticking this box indicates you have read and understood the above declaration",
            required=True,
            error_messages={"required": "Please check the tick box to accept the declaration"},
            widget=forms.CheckboxInput(attrs={"class": "govuk-checkbox", "data-testid": "declaration-checkbox"}),
        )

        fieldset_additions.append("declaration")

        return Fieldset(*fieldset_additions, legend="Declarations", legend_tag="h2", legend_size="s")

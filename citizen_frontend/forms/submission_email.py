from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Field, Layout
from django import forms


class SubmissionEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        help_text="Please provide your email address, "
        "so the licensing authority can let you know if your application has been successful or not.",
        error_messages={
            "required": "Please provide your email address",
            "invalid": "Enter an email address in the correct format, like name@example.com",
        },
        widget=forms.TextInput(attrs={"data-testid": "email-field"}),
    )

    def __init__(self, context):
        super().__init__()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.text("email", autocomplete="email"),
        )

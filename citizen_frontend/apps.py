from django.apps import AppConfig
from django.db import models


class CitizenFrontendConfig(AppConfig):
    name = "citizen_frontend"

    # Check tests for concrete example of issue being patched
    def _patch_django_mongodb_backend_to_accept_nullable_nested_embedded_models(self):
        from django_mongodb_backend.fields import EmbeddedModelField

        original_validate = EmbeddedModelField.validate
        # this is so we can test the original bug still exists, and if it doesnt we can delete this whole patch
        EmbeddedModelField._original_validate = original_validate

        # when a field is None, do a regular django  model validate just in case then if it's marked as nullable
        # it return as there's no need to validate further. The original method fails as it checks the fields type
        # against the fields instance  type to see if it matches the expected myEmbeddedModelField EmbeddedModelField
        # ...which it doesn't because it's None which is totally fine when marked as nullable.
        def patched_validate(self, value, model_instance):
            if value is None:
                models.Field.validate(self, value, model_instance)
                if self.null:
                    return
            original_validate(self, value, model_instance)

        EmbeddedModelField.validate = patched_validate

    def ready(self):
        self._patch_django_mongodb_backend_to_accept_nullable_nested_embedded_models()

from django.apps import AppConfig


class CitizenFrontendConfig(AppConfig):
    name = "citizen_frontend"

    def ready(self):
        from common.patches.embedded_model_field_patch import (
            patch_django_mongodb_backend_to_accept_nullable_nested_embedded_models,
        )

        patch_django_mongodb_backend_to_accept_nullable_nested_embedded_models()

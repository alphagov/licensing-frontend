from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence
from common.models.licence_application import LicenceApplication

from citizen_frontend.repository.department_repository import DepartmentRepository


def licence_submission_success_page(
    application: LicenceApplication, licence: Licence, authority, customisation: Customisation
):
    has_supporting_documents = customisation.supporting_document_definitions
    all_supporting_documents_required = has_supporting_documents and all_docs_mandatory(customisation)
    processing_days = format_processing_days(customisation)
    department = get_department(authority)

    context = {
        "licence_name": licence.name,
        "authority": authority,
        "published_customisation": customisation,
        "application": application,
        "has_supporting_documents": has_supporting_documents,
        "all_supporting_documents_required": all_supporting_documents_required,
        "processing_days": processing_days,
        "is_paid": False,
        "department": department,
        "step": "4" if customisation.is_fee_required else "3",
    }
    if application.expected_processing_date:
        formatted_expected_processing_date = application.expected_processing_date.strftime("%d %B %Y")
        context.update(
            {
                "expected_processing_date": formatted_expected_processing_date,
            }
        )
    return context


def get_department(authority: Authority):
    department_repo = DepartmentRepository()
    department = department_repo.get_department_from_authority_slug(authority.url_slug)
    return department


def format_processing_days(customisation: Customisation):
    number = customisation.number_of_days_to_process
    day_type = "working" if customisation.is_processing_days_working_days else "calendar"
    unit = "days" if number > 1 else "day"
    return f"{number} {day_type} {unit}"


# TODO: move this to customisation model?


def all_docs_mandatory(customisation: Customisation):
    docs = customisation.supporting_document_definitions
    return bool(docs) and all(doc.is_mandatory for doc in docs)


# TODO: move this to customisation model?

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class LicenceResponse(BaseModel):
    code: str
    name: str
    legislation: list[str]


class AuthorityContactDetails(BaseModel):
    website: str
    email: str
    phone: str
    address: str


class AuthorityInteraction(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)

    url: str = ""
    uses_licensify: bool
    uses_authority_url: bool
    description: str
    payment: str
    payment_amount: str | None = None
    introduction_text: str


class IssuingAuthority(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)

    authority_name: str
    authority_slug: str
    authority_contact: AuthorityContactDetails
    authority_interactions: dict[str, list[AuthorityInteraction]]


class LicenceAuthoritiesAndInteractionsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True)

    is_location_specific: bool
    is_offered_by_county: bool
    geographical_availability: list[str]
    issuing_authorities: list[IssuingAuthority]

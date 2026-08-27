from pydantic import BaseModel


class LicenceResponse(BaseModel):
    code: str
    name: str
    legislation: list[str]

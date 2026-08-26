from pydantic import BaseModel


# do we need these if we do a clean on the data that we pull from db?
class LicenceResponse(BaseModel):
    code: str
    name: str
    legislation: str

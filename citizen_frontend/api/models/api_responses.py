from pydantic import BaseModel


# do we need these if we do a clean on the data that we pull from db?
# lot of cleaning...
class LicenceResponse(BaseModel):
    code: str
    name: str
    legislation: list[str]

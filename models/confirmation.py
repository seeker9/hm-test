from pydantic import BaseModel


class Confirmation(BaseModel):
    client_id: str
    reservation_id: str
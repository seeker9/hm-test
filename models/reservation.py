from pydantic import BaseModel


class Reservation(BaseModel):
    client_id: str
    slot_id: str
    slot_datetime: str
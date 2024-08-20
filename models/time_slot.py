from pydantic import BaseModel


class TimeSlot(BaseModel):
    slot_id: str
    slot_datetime: str
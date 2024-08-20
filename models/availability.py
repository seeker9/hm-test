from pydantic import BaseModel


class Availability(BaseModel):
    provider_id: str
    start_time: str
    end_time: str
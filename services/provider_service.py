from datetime import datetime, timedelta
from uuid import uuid4

from models.time_slot import TimeSlot


class ProviderService:
    def __init__(self):
        # simplified as in-memory storage
        self.providers = {}
    
    def fetch_all(self):
        return self.providers
    
    def find_slots_by_provider(self, provider_id: str):
        return self.providers.get(provider_id, None)
    
    def add_slots(self, provider_id: str, start: datetime, end: datetime):
        if provider_id not in self.providers:
            self.providers[provider_id] = []
        slots = []
        current_time = start
        # Assumption: if not enough time for 15-min slot, cut off the tail
        while current_time + timedelta(minutes=15) <= end:
            slots.append(
                TimeSlot(
                    slot_id=str(uuid4()),
                    slot_datetime=current_time.strftime("%Y-%m-%d %H:%M")
                )
            )
            current_time += timedelta(minutes=15)
        self.providers[provider_id].extend(slots)
        return slots
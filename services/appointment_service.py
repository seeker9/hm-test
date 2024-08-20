from datetime import datetime
from typing import Union

class AppointmentService:
    def __init__(self):
        # simplified as in-memory storage
        self.appointments = {}

    def clean_expired_reservations(self):
        now = datetime.now()
        for slot_id in self.appointments:
            curr_appt = self.appointments[slot_id]
            if curr_appt['reserved'] and (now - curr_appt['reserved_at']).seconds > 1800:  # 30 minutes
                curr_appt['reserved'] = False
                curr_appt['reserved_by'] = None
                curr_appt['reserved_at'] = None

    def fetch_all(self):
        return self.appointments

    def get_by_id(self, appt_id: str):
        return self.appointments.get(appt_id, None)

    def upinsert(self, appt_id: str, reserved: bool, reserved_by: Union[str, None] = None, reserved_at: Union[datetime, None] = None):
        if appt_id not in self.appointments:
            self.appointments[appt_id] = {}
        self.appointments[appt_id] = {
            reserved: reserved,
        }
        if reserved_by:
            self.appointments[appt_id]['reserved_by'] = reserved_by
        if reserved_at:
            self.appointments[appt_id]['reserved_at'] = reserved_at
    

    

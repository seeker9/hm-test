from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import List

from models.time_slot import TimeSlot
from models.availability import Availability
from models.confirmation import Confirmation
from models.reservation import Reservation
from services.appointment_service import AppointmentService
from services.provider_service import ProviderService

app = FastAPI()

appointment_service = AppointmentService()
provider_service = ProviderService()

# Routes
@app.post("/provider/availability")
def add_availability(availability: Availability):
    provider_id = availability.provider_id
    start_time = datetime.strptime(availability.start_time, "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(availability.end_time, "%Y-%m-%d %H:%M")
    slots = provider_service.add_slots(provider_id=provider_id, start=start_time, end=end_time)
    for slot in slots:
        appointment_service.upinsert(
            appt_id=slot.slot_id,
            reserved=False,
            reserved_at="",
            reserved_by=""
        )

    return {"message": "Availability added successfully."}

@app.get("/client/available_slots", response_model=List[TimeSlot])
def get_available_slots(provider_id: str):
    if provider_id not in provider_service.fetch_all():
        raise HTTPException(status_code=404, detail="Provider not found")

    return _find_available_slots_by_provider(provider_id=provider_id)

@app.post("/client/reserve_slot")
def reserve_slot(reservation: Reservation):
    slot_id = reservation.slot_id
    slot_time = reservation.slot_datetime
    client_id = reservation.client_id
    appointment_service.clean_expired_reservations()
    appt = appointment_service.get_by_id(slot_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Invalid Slot")

    if appt['reserved']:
        raise HTTPException(status_code=409, detail="Slot already reserved")

    reservation_time = datetime.strptime(slot_time, "%Y-%m-%d %H:%M") - timedelta(hours=24)
    if datetime.now() > reservation_time:
        raise HTTPException(status_code=400, detail="Reservations must be made at least 24 hours in advance")
    
    appointment_service.upinsert(
        appt_id=slot_id,
        reserved=True,
        reserved_by=client_id,
        reserved_at=datetime.now()
    )

    return {"message": "Slot reserved successfully.", "reservation_id": slot_id}

@app.post("/client/confirm_reservation")
def confirm_reservation(confirmation: Confirmation):
    slot_id = confirmation.reservation_id
    client_id = confirmation.client_id
    appointment_service.clean_expired_reservations()
    appt = appointment_service.get_by_id(slot_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if appt['reserved_by'] != client_id:
        raise HTTPException(status_code=403, detail="Invalid client")

    appointment_service.upinsert(
        appt_id=slot_id,
        reserved=True
    )

    return {"message": "Reservation confirmed successfully."}


def _find_available_slots_by_provider(provider_id: str) -> List[TimeSlot]:
    appointment_service.clean_expired_reservations()
    available_slots = []
    potential_slots = provider_service.find_slots_by_provider(provider_id=provider_id)
    for slot in potential_slots:
        appt = appointment_service.get_by_id(slot.slot_id)
        if not appt or not appt['reserved']:
            available_slots.append(slot.slot_datetime)
    
    return available_slots

# Start the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9981)

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime
import json

# Mock in-memory database
appointments_db = []

class DatabaseInput(BaseModel):
    """Input schema for DatabaseTool."""
    action: str = Field(..., description="Action to perform: 'check_availability' or 'save_appointment'")
    patient_name: str = Field(None, description="Name of the patient")
    appointment_time: str = Field(None, description="Preferred appointment time in ISO format (e.g., '2025-06-23T10:00:00')")
    specialty: str = Field(None, description="Doctor specialty (e.g., 'Cardiology')")

class DatabaseTool(BaseTool):
    name: str = "DatabaseTool"
    description: str = "Tool to check appointment availability or save an appointment in the hospital database."
    args_schema: type[BaseModel] = DatabaseInput

    def _run(self, action: str, patient_name: str = None, appointment_time: str = None, specialty: str = None) -> str:
        if action == "check_availability":
            try:
                requested_time = datetime.fromisoformat(appointment_time)
                # Check if the slot is taken
                for appt in appointments_db:
                    if appt["appointment_time"] == appointment_time and appt["specialty"] == specialty:
                        return json.dumps({"available": False, "message": "Slot is already booked."})
                return json.dumps({"available": True, "message": "Slot is available."})
            except ValueError:
                return json.dumps({"available": False, "message": "Invalid date format."})

        elif action == "save_appointment":
            try:
                appointment = {
                    "patient_name": patient_name,
                    "appointment_time": appointment_time,
                    "specialty": specialty
                }
                appointments_db.append(appointment)
                return json.dumps({"success": True, "message": f"Appointment saved for {patient_name} at {appointment_time} with {specialty}."})
            except Exception as e:
                return json.dumps({"success": False, "message": f"Error saving appointment: {str(e)}"})

        else:
            return json.dumps({"success": False, "message": "Invalid action."})
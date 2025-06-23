import gradio as gr
from datetime import datetime, timedelta
import pytz # For timezone awareness
import os

from hospital_scheduler.crew import HospitalSchedulerCrew

# --- Configuration ---
# Ensure your OPENAI_API_KEY is set as an environment variable
# Example: os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
# For local development, it's best to set this in your system environment
# or use a .env file and load it (e.g., with python-dotenv)

# Define the local timezone for appointment scheduling
local_timezone = pytz.timezone('America/New_York') # Oshawa is in this timezone

# --- Core Function to Run CrewAI ---
def schedule_appointment(
    patient_name: str,
    reason_for_visit: str,
    appointment_date: datetime, # Gradio passes datetime.date objects for date inputs
    appointment_time_str: str,
    doctor_specialty: str
):
    """
    This function takes inputs from the Gradio UI, formats them for CrewAI,
    and then runs the HospitalSchedulerCrew.
    """
    if not all([patient_name, reason_for_visit, appointment_date, appointment_time_str, doctor_specialty]):
        return "Error: Please fill in all required fields."

    try:
        # Combine date and time into a timezone-aware datetime object
        time_parts = list(map(int, appointment_time_str.split(':')))
        if len(time_parts) != 2 or not (0 <= time_parts[0] <= 23) or not (0 <= time_parts[1] <= 59):
            return "Error: Invalid time format. Please use HH:MM (e.g., 09:00)."

        combined_datetime_naive = datetime(
            appointment_date.year,
            appointment_date.month,
            appointment_date.day,
            time_parts[0],
            time_parts[1]
        )
        local_dt = local_timezone.localize(combined_datetime_naive, is_dst=None) # is_dst=None lets pytz figure it out

        # Convert to ISO 8601 string (with timezone offset) for the bot
        iso_datetime_str = local_dt.isoformat()

        # Construct the patient input string for the CrewAI bot
        patient_input_for_bot = (
            f"Patient Name: {patient_name}\n"
            f"Reason for Visit: {reason_for_visit}\n"
            f"Preferred Appointment Date/Time: {iso_datetime_str}\n"
            f"Preferred Doctor Specialty: {doctor_specialty}"
        )

        print(f"\n[Gradio App] Input to CrewAI:\n{patient_input_for_bot}\n") # For terminal visibility

        # Initialize and run the CrewAI logic
        crew = HospitalSchedulerCrew(patient_input_for_bot)
        crew_output = crew.kickoff()

        return crew_output

    except Exception as e:
        # Log the error for debugging
        print(f"\n[Gradio App Error] {e}")
        return f"An error occurred: {str(e)}"

# --- Gradio Interface Setup ---

# Set default date to tomorrow for convenience
default_date = datetime.now(local_timezone).date() + timedelta(days=1)

# Define Gradio Interface components
inputs = [
    gr.Textbox(label="Patient Name", placeholder="e.g., John Doe"),
    gr.Textbox(label="Reason for visit / Desired Service", placeholder="e.g., General health checkup"),
    gr.Date(label="Preferred Date", value=default_date, interactive=True), # Date picker
    gr.Textbox(label="Preferred Time (HH:MM)", placeholder="e.g., 09:00, 14:30"), # Text for time
    gr.Textbox(label="Preferred Doctor Specialty", placeholder="e.g., Cardiology, Pediatrics, General"),
]

outputs = gr.Markdown(label="AI Agent Response") # Use Markdown to render rich text output

# Create the Gradio Interface
iface = gr.Interface(
    fn=schedule_appointment,
    inputs=inputs,
    outputs=outputs,
    title="🏥 Hospital Appointment Scheduler (Gradio)",
    description="Enter patient details to schedule an appointment with our AI assistant.",
    allow_flagging="never", # Prevents user from 'flagging' outputs
    theme=gr.themes.Soft() # A softer theme
)

# Launch the Gradio app
if __name__ == "__main__":
    # Ensure your API key is set before launching the app
    # For local development, you might set it here temporarily for testing:
    # os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
    # It's better practice to set it outside the script (e.g., .env file or system env vars)

    iface.launch(
        server_name="0.0.0.0", # Allows access from other devices on your local network
        server_port=7860,    # Default Gradio port, choose another if 7860 is busy
        # share=True         # Uncomment to generate a public shareable link (temporary)
    )
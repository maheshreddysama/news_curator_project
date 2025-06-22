import os
from datetime import datetime
import pytz # Make sure you have this installed: pip install pytz

from hospital_scheduler.crew import HospitalSchedulerCrew

def run():
    print("\n--- Hospital Appointment Scheduler (Terminal Mode) ---")

    # 1. Get Patient Name
    patient_name = input("Enter Patient Name: ")
    if not patient_name:
        print("Patient Name cannot be empty. Exiting.")
        return

    # 2. Get Reason for Visit
    reason_for_visit = input("Enter Reason for visit / Desired Service: ")
    if not reason_for_visit:
        print("Reason for visit cannot be empty. Exiting.")
        return

    # 3. Get Preferred Date
    while True:
        date_str = input("Enter Preferred Date (YYYY-MM-DD, e.g., 2025-06-25): ")
        try:
            preferred_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    # 4. Get Preferred Time
    while True:
        time_str = input("Enter Preferred Time (HH:MM, e.g., 09:00 or 14:30): ")
        try:
            time_parts = list(map(int, time_str.split(':')))
            if len(time_parts) == 2 and 0 <= time_parts[0] <= 23 and 0 <= time_parts[1] <= 59:
                preferred_time = datetime.strptime(time_str, "%H:%M").time()
                break
            else:
                print("Invalid time format. Please use HH:MM.")
        except ValueError:
            print("Invalid time format. Please use HH:MM.")

    # 5. Get Preferred Doctor Specialty
    doctor_specialty = input("Enter Preferred Doctor Specialty (e.g., Cardiology, Pediatrics, General): ")
    if not doctor_specialty:
        print("Doctor Specialty cannot be empty. Exiting.")
        return

    # Combine date and time into an ISO format string
    # Using current location time zone (Oshawa, Ontario, Canada is EDT currently)
    local_timezone = pytz.timezone('America/New_York') # Oshawa is in this timezone

    # Create a naive datetime object
    combined_datetime_naive = datetime.combine(preferred_date, preferred_time)

    # Make the datetime timezone-aware
    # Using 'localize' for local time
    local_dt = local_timezone.localize(combined_datetime_naive, is_dst=None) # is_dst=None lets pytz figure it out

    # Convert to ISO 8601 string (with timezone offset)
    iso_datetime_str = local_dt.isoformat()

    # Construct the patient input string for the CrewAI bot
    patient_input_for_bot = (
        f"Patient Name: {patient_name}\n"
        f"Reason for Visit: {reason_for_visit}\n"
        f"Preferred Appointment Date/Time: {iso_datetime_str}\n"
        f"Preferred Doctor Specialty: {doctor_specialty}"
    )

    print("\n--- Input provided to the AI Agent ---")
    print(patient_input_for_bot)
    print("---------------------------------------")

    try:
        crew = HospitalSchedulerCrew(patient_input_for_bot)
        result = crew.kickoff()

        print("\n\n########################")
        print("## Here is the Final Result from the AI Agent")
        print("########################\n")
        print(result)
        print("\n--- End of Crew Execution ---")

    except Exception as e:
        print(f"\nERROR: An error occurred while running the crew: {e}")
        # Optionally, print the full traceback for debugging:
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    # Ensure your OPENAI_API_KEY is set as an environment variable
    # For testing, you could uncomment the line below and put your key.
    # NEVER commit your API key directly into code in a real project!
    # os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY_HERE"

    run()
import yaml
from crewai import Crew, Process, Agent, Task
from hospital_scheduler.tools.database_tool import DatabaseTool
from pathlib import Path
from langchain_openai import ChatOpenAI # CORRECTED: Import ChatOpenAI from langchain_openai

class HospitalSchedulerCrew:
    def __init__(self, patient_input: str):
        self.patient_input = patient_input
        #self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_dir = Path(__file__).parent / "config"
        try:
            with open(self.config_dir / "agents.yaml", "r") as f:
                self.agents_data = yaml.safe_load(f)
            with open(self.config_dir / "tasks.yaml", "r") as f:
                self.tasks_data = yaml.safe_load(f)

            if not isinstance(self.agents_data, dict) or "scheduler" not in self.agents_data or not isinstance(self.agents_data["scheduler"], dict):
                raise ValueError("agents.yaml did not load correctly or 'scheduler' is missing/invalid.")
            if not isinstance(self.agents_data, dict) or "database_agent" not in self.agents_data or not isinstance(self.agents_data["database_agent"], dict):
                raise ValueError("agents.yaml did not load correctly or 'database_agent' is missing/invalid.")
            if not isinstance(self.tasks_data, dict) or "collect_details_task" not in self.tasks_data or not isinstance(self.tasks_data["collect_details_task"], dict):
                raise ValueError("tasks.yaml did not load correctly or 'collect_details_task' is missing/invalid.")
            if not isinstance(self.tasks_data, dict) or "manage_booking_task" not in self.tasks_data or not isinstance(self.tasks_data["manage_booking_task"], dict):
                raise ValueError("tasks.yaml did not load correctly or 'manage_booking_task' is missing/invalid.")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found: {e}. Looked in: {self.config_dir}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")

    def setup_crew(self) -> Crew:
        scheduler_config = self.agents_data["scheduler"]
        database_agent_config = self.agents_data["database_agent"]
        collect_details_task_config = self.tasks_data["collect_details_task"]
        manage_booking_task_config = self.tasks_data["manage_booking_task"]

        # Instantiate LLMs using ChatOpenAI
        scheduler_llm = ChatOpenAI(model_name=scheduler_config.get("llm", "gpt-4o-mini"))
        database_agent_llm = ChatOpenAI(model_name=database_agent_config.get("llm", "gpt-4o-mini"))

        scheduler = Agent(
            role=scheduler_config["role"],
            goal=scheduler_config["goal"],
            backstory=scheduler_config["backstory"],
            verbose=scheduler_config.get("verbose", False),
            allow_delegation=scheduler_config.get("allow_delegation", False),
            llm=scheduler_llm,
            tools=[DatabaseTool()]
        )
        database_agent = Agent(
            role=database_agent_config["role"],
            goal=database_agent_config["goal"],
            backstory=database_agent_config["backstory"],
            verbose=database_agent_config.get("verbose", False),
            allow_delegation=database_agent_config.get("allow_delegation", False),
            llm=database_agent_llm,
            tools=[DatabaseTool()]
        )

        collect_details_task = Task(
            description=collect_details_task_config["description"],
            expected_output=collect_details_task_config["expected_output"],
            agent=scheduler,
            tools=[DatabaseTool()],
            human_input=collect_details_task_config.get("human_input", False)
        )

        manage_booking_task = Task(
            description=manage_booking_task_config["description"],
            expected_output=manage_booking_task_config["expected_output"],
            agent=database_agent,
            tools=[DatabaseTool()],
            human_input=manage_booking_task_config.get("human_input", False)
        )

        return Crew(
            agents=[scheduler, database_agent],
            tasks=[collect_details_task, manage_booking_task],
            process=Process.sequential,
            verbose=True
        )

    def kickoff(self):
        crew = self.setup_crew()
        result = crew.kickoff(inputs={"patient_input": self.patient_input})
        return result
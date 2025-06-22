import yaml
from pathlib import Path

config_dir = Path("src/hospital_scheduler/config")
with open(config_dir / "tasks.yaml", "r") as f:
    tasks_config = yaml.safe_load(f)
print(type(tasks_config))  # Should print <class 'dict'>
print(tasks_config.keys())  # Should print dict_keys(['collect_details_task', 'manage_booking_task'])
print(type(tasks_config["collect_details_task"]))  # Should print <class 'dict'>
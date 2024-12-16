from datetime import datetime
from config.config_components.logs_collector_schema import TaskLogEntry
from config.config_components import CollectorType
from helpers import validate_attribute


def data_formatter(task: object, system_info: dict, environment: dict) -> list:
    collector_type = validate_attribute(task, "type", CollectorType)
    match collector_type:
        case CollectorType.BASH: return format_bash_data(task, system_info, environment)
        case CollectorType.LOGS: return format_logs_data(task, system_info, environment)
        case _: raise NotImplementedError(f"Data formatter for {collector_type} not implemented yet")


def format_bash_data(task: object, system_info: dict, environment) -> list:
    task_result = validate_attribute(task, "task_result", object)
    task_type = validate_attribute(task, "type", CollectorType).name
    task_name = validate_attribute(task, "name", str)
    return [
        {
            "_time": datetime.now().isoformat(),
            "agent": {
                "type": task_type,
                "name": task_name,
                "system_info": system_info,
                "environment": environment,
            },
            "task_result": task_result.__dict__,
        }
    ]


def format_logs_data(task: object, system_info: dict, environment) -> list:
    task_logs = validate_attribute(task, "task_result", object)
    task_type = validate_attribute(task, "type", CollectorType).name
    task_name = validate_attribute(task, "name", str)

    formatted_logs = []
    for log_entries in task_logs:
        if not isinstance(log_entries, TaskLogEntry):
            raise TypeError(f"Expected TaskLogEntry, got {type(log_entries)}")
        for log_message in log_entries:

            log_entry = {
                "_time": datetime.now().isoformat(),
                "agent": {
                    "type": task_type,
                    "name": task_name,
                    "system_info": system_info,
                    "environment": environment,
                },
                "log_message": log_message,
                "log_file_path": log_entries.path,
            }
            formatted_logs.append(log_entry)

    return formatted_logs

from task_manager.task_components import Task
from config.config_components.bash_collector_schema import BashIndex, TaskBashResult, TaskBash
import subprocess


def handle_data_collection(task: Task):
    if not isinstance(task.current_task, TaskBash) or not isinstance(task.indexed_data, BashIndex):
        raise ValueError(f"Task {task.name} is not a bash collector and have {task.indexed_data} indexed data.")
    if task.current_task.args or task.current_task.kwargs:
        raise NotImplementedError("Arguments and keyword arguments are not supported for bash collectors.")
    cmd = task.current_task.command
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    task.task_result = TaskBashResult(stdout=result.stdout, stderr=result.stderr)
    return task

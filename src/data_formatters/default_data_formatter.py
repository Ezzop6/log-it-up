# This is default data formatter for before sent request
from helpers import validate_attribute


def data_formatter(task: object) -> dict:
    task_result = validate_attribute(task, "task_result", object)
    return task_result.__dict__

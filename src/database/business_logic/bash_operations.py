from task_manager.task_components import Task
from config.config_components import BashIndex, TaskBash, TaskBashResult
from peewee import DoesNotExist


def get_bash_indexes(task: Task):
    from ..models import BashCollectorModel, BashTaskModel
    try:
        collector = BashCollectorModel.get(BashCollectorModel.id == task.task_id)
        task_entries = BashTaskModel.get(BashTaskModel.collector == collector)
        return BashIndex(index=task_entries.task_index)
    except DoesNotExist:
        collector = get_or_create_bash_collector(task)
        task_entries = get_or_create_bash_task(task)
    return BashIndex(index='')


def get_or_create_bash_collector(task: Task):
    from ..models import BashCollectorModel
    collector, created = BashCollectorModel.get_or_create(id=task.task_id, name=task.name, type=task.type)
    return collector


def get_or_create_bash_task(task: Task):
    if not isinstance(task.current_task, TaskBash):
        raise ValueError(f"Task {task.task_id} is not a bash collector.")
    from ..models import BashTaskModel, BashCollectorModel

    collector = BashCollectorModel.get(BashCollectorModel.id == task.task_id)
    try:
        bash_task = BashTaskModel.get(
            (BashTaskModel.collector == collector) &
            (BashTaskModel.task == task.current_task.command)
        )
    except DoesNotExist:
        bash_task = BashTaskModel.create(
            collector=collector,
            task=task.current_task.command,
            task_index='',
        )
    return bash_task


def record_bash_result(task: Task):
    if not isinstance(task.current_task, TaskBash):
        raise ValueError(f"Task {task.task_id} is not a bash collector.")
    if not isinstance(task.task_result, TaskBashResult):
        raise ValueError(f"Task {task.task_id} does not have a result.")
    if not isinstance(task.indexed_data, BashIndex):
        raise ValueError(f"Task {task.task_id} does not have indexed data.")

    from ..models import BashCollectorModel, BashTaskModel, BashResultModel
    collector = BashCollectorModel.get(BashCollectorModel.id == task.task_id)
    current_task = BashTaskModel.get(
        (BashTaskModel.collector == collector) &
        (BashTaskModel.task == task.current_task.command)
    )
    BashResultModel.create(
        collector=collector,
        task=current_task,
        stdout=task.task_result.stdout,
        stderr=task.task_result.stderr,
    )

    current_task.update_index(task)

    return current_task

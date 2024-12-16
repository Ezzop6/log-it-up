from task_manager.task_components import Task
from config.config_components import TaskLog, LogFileIndex, LogFilesMapping, TaskLogResult
from peewee import DoesNotExist # type: ignore


def get_log_indexes(task: Task) -> LogFilesMapping:
    from ..models import PathModel, LogCollectorModel
    try:
        collector = LogCollectorModel.get(LogCollectorModel.id == task.task_id)

        existing_path_entries = PathModel.select().where(PathModel.collector == collector)
        existing_paths = set(path_entry.path for path_entry in existing_path_entries)

        if not isinstance(task.current_task, TaskLog):
            raise ValueError(f"Task {task.task_id} is not a log collector.")

        new_paths = set(task.current_task.paths) - existing_paths
        if new_paths:
            from utils import FileWatcher
            for new_path in new_paths:
                file = FileWatcher()._get_metadata(new_path)
                PathModel.create(
                    collector=collector,
                    path=new_path,
                    path_index=file.lines,
                    inode=file.inode,
                    size=file.size,
                    last_modified=file.last_modified
                )

        path_entries = PathModel.select().where(PathModel.collector == collector)

        return LogFilesMapping(
            total_runs=path_entries[0].total_runs if path_entries else 0,
            index=[
                LogFileIndex(
                    path=path_entry.path,
                    index=path_entry.path_index,
                    inode=path_entry.inode,
                    size=path_entry.size,
                    last_modified=path_entry.last_modified
                )
                for path_entry in path_entries
            ],
        )

    except DoesNotExist:
        collector = get_or_create_collector(task)
        path_entries = get_or_create_path(task)
        return LogFilesMapping(index=[
            LogFileIndex(path=path_entry.path, index=0)
            for path_entry in path_entries
        ])


def get_or_create_collector(task: Task):
    from ..models import LogCollectorModel
    collector, created = LogCollectorModel.get_or_create(id=task.task_id, name=task.name, type=task.type)
    return collector


def get_or_create_path(task: Task):
    if not isinstance(task.current_task, TaskLog):
        raise ValueError(f"Task {task.task_id} is not a log collector.")
    from ..models import PathModel, LogCollectorModel

    collector = LogCollectorModel.get(LogCollectorModel.id == task.task_id)

    path_entries = []
    for path in task.current_task.paths:
        try:
            path_entry = PathModel.get(
                (PathModel.collector == collector) &
                (PathModel.path == path)
            )
        except DoesNotExist:
            from utils import FileWatcher
            file = FileWatcher().get_metadata(path)
            path_entry = PathModel.create(
                collector=collector,
                path=path,
                path_index=file.index,
                inode=file.inode,
                size=file.size,
                last_modified=file.last_modified
            )

        path_entries.append(path_entry)

    return path_entries


def add_log_line(task: Task):
    if not isinstance(task.task_result, TaskLogResult):
        raise ValueError(f"Task {task.task_id} is not a log collector.")
    if not isinstance(task.indexed_data, LogFilesMapping):
        raise ValueError(f"Task {task.task_id} does not have indexed data.")

    from ..models import LogLineModel, LogCollectorModel, PathModel
    collector = LogCollectorModel.get(LogCollectorModel.id == task.task_id)

    log_lines_to_create = []
    paths_to_update = {}

    for log_entry in task.task_result:
        path_entry = PathModel.get(
            (PathModel.collector == collector) &
            (PathModel.path == log_entry.path)
        )

        entry_log_lines = [
            LogLineModel(
                collector=collector,
                path=path_entry,
                message=message
            )
            for message in log_entry.messages
            if message
        ]
        log_lines_to_create.extend(entry_log_lines)

        paths_to_update[log_entry.path] = task.indexed_data.get_data(log_entry.path)

    if log_lines_to_create:
        LogLineModel.bulk_create(log_lines_to_create)

    for path, log_file_index in paths_to_update.items():
        path_entry = PathModel.get(
            (PathModel.collector == collector) &
            (PathModel.path == path)
        )
        path_entry.update_index(log_file_index)

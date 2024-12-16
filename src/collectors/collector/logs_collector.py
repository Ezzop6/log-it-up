from task_manager.task_components import Task
from pathlib import Path
from config.config_components.logs_collector_schema import TaskLogResult, TaskLogEntry, TaskLog, LogFileIndex, LogFilesMapping
from pprint import pprint
from utils.file_watcher import FileWatcher, FileStatus


def handle_data_collection(task: Task):
    if not isinstance(task.current_task, TaskLog) or not isinstance(task.indexed_data, LogFilesMapping):
        raise ValueError(f"Task {task.name} is not a log collector and have {task.indexed_data} indexed data.")
    task.task_result = TaskLogResult()
    if task.current_task.full_file and task.indexed_data.total_runs == 0:
        # TODO: Change this Find better way to handle this
        for path in task.current_task.paths:
            meta_data = FileWatcher().get_metadata(Path(path))
            lines = get_new_lines(Path(path), 0)
            task.task_result.logs.append(TaskLogEntry(path=path, messages=lines[0], is_successful=lines[2]))
            task.indexed_data.update_index(LogFileIndex(
                path=path,
                index=meta_data.index,
                inode=meta_data.inode,
                size=meta_data.size,
                last_modified=meta_data.last_modified
            ))
        return task

    for path in task.current_task.paths:
        indexed_data = task.indexed_data.get_data(path)
        status = FileWatcher().check_file_status(indexed_data, Path(path))

        if status in [FileStatus.REPLACED, FileStatus.TRUNCATED]:
            meta_data = FileWatcher().get_metadata(Path(path))
            task.indexed_data.update_index(LogFileIndex(path=path, index=0, inode=meta_data.inode, size=meta_data.size, last_modified=meta_data.last_modified))
            status = FileStatus.UNCHANGED

        if status == FileStatus.UNCHANGED:
            continue

        meta_data = FileWatcher().get_metadata(Path(path))
        messages, index, is_successful = get_new_lines(Path(path), task.indexed_data.get_index(path))
        task.task_result.logs.append(TaskLogEntry(path=path, messages=messages, is_successful=is_successful))
        task.indexed_data.update_index(LogFileIndex(
            path=path,
            index=index,
            inode=meta_data.inode,
            size=meta_data.size,
            last_modified=meta_data.last_modified
        ))
    return task


def get_new_lines(path: Path, index: int) -> tuple[list, int, bool]:
    try:
        file = path.open()
        lines = []
        for line in file.readlines()[index:]:
            lines.append(line)
        new_index = len(lines) + index
        file.close()
        return lines, new_index, True
    except Exception as e:
        from utils.logger import log_record, logging
        # TODO: What should be done in case of an error?
        log_record(f"Error reading log file {path}: {e}", level=logging.ERROR)
        return [], index, False


def get_file_index(path: Path) -> int:
    try:
        file = path.open()
        lines = file.readlines()
        file.close()
        return len(lines)
    except Exception as e:
        from utils.logger import log_record, logging
        log_record(f"Error reading log file {path}: {e}", level=logging.ERROR)
        return 0

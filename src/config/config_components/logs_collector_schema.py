from dataclasses import dataclass, field
from marshmallow import Schema, fields, EXCLUDE, post_load
from typing import List


@dataclass
class LogFileIndex:
    path: str = field(default="")
    index: int = field(default=0)
    inode: int = field(default=0)
    size: int = field(default=0)
    last_modified: float = field(default=0)


@dataclass
class LogFilesMapping:
    index: List[LogFileIndex] = field(default_factory=list)
    total_runs: int = field(default=0)

    def __iter__(self):
        return iter(self.index)

    def get_data(self, input_path: str) -> LogFileIndex:
        for log_file_index in self.index:
            if input_path == log_file_index.path:
                return log_file_index
        return LogFileIndex()

    def get_index(self, input_path: str) -> int:
        for log_file_path in self.index:
            if input_path == log_file_path.path:
                return log_file_path.index
        return 0

    def update_index(self, data: LogFileIndex) -> None:
        for log_file_path in self.index:
            if data.path == log_file_path.path:
                log_file_path.index = data.index
                log_file_path.inode = data.inode
                log_file_path.size = data.size
                log_file_path.last_modified = data.last_modified
                return


@dataclass
class TaskLogEntry:
    path: str = field(default_factory=str)
    messages: list[str] = field(default_factory=list)
    is_successful: bool = field(default=False)

    def __iter__(self):
        return iter(self.messages)


@dataclass
class TaskLogResult:
    logs: list[TaskLogEntry] = field(default_factory=list)

    def __iter__(self):
        return iter(self.logs)


@dataclass
class TaskLog:
    paths: list[str] = field(default_factory=list)
    full_file: bool = field(default=False)

    class Meta:
        unknown = EXCLUDE


class TaskLogSchema(Schema):
    paths = fields.List(fields.Str(), required=False, allow_none=True, missing=[])
    full_file = fields.Bool(required=False, allow_none=True, missing=False)

    @post_load
    def make_task_log(self, data, **kwargs):
        return TaskLog(**data)

    class Meta:
        unknown = EXCLUDE

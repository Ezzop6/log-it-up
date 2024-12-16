from marshmallow import Schema, fields, EXCLUDE
from dataclasses import dataclass, field
from helpers import calculate_time_seconds, get_persistent_hash, find_paths_by_pattern, MatchingPattern
from typing import List
from enum import Enum
from .logs_collector_schema import TaskLog, TaskLogSchema, LogFilesMapping
from .bash_collector_schema import TaskBash, TaskBashSchema, BashIndex


class CollectorFilterType(Enum):
    NONE = "NONE"
    REGEX = "REGEX"


class CollectorType(Enum):
    NONE = "none"
    LOGS = "logs"
    BASH = "bash"
    BASH_SCRIPT = "bash_script"
    CUSTOM_SCRIPT = "custom_script"

    def get_collector_types(self) -> List[str]:
        return [collector_type.value for collector_type in CollectorType]


@dataclass
class BaseCollector:
    send_interval: int = field(default=-1) # -1 means auto send interval (send data as soon as possible) TODO: Add support for auto send interval
    name: str = field(default_factory=str)
    type: CollectorType = field(default=CollectorType.NONE)
    filter: CollectorFilterType = field(default=CollectorFilterType.NONE)
    id: int = field(default_factory=int)


class BaseCollectorSchema(Schema):
    send_interval = fields.Method(
        required=True,
        deserialize="deserialize_send_interval"
    )

    id = fields.Int(required=False, allow_none=True)
    name = fields.Str(required=True, allow_none=False)
    type = fields.Enum(CollectorType, by_value=True, required=True)
    filter = fields.Enum(CollectorFilterType, by_value=True, required=False, missing=CollectorFilterType.NONE, allow_none=True)

    def deserialize_send_interval(self, value: str) -> int:
        return calculate_time_seconds(value)

    def load(self, data, *args, **kwargs):
        if "id" not in data or not data["id"]:
            # TODO: Find a better way to generate id
            data["id"] = get_persistent_hash(f"{data['name']}_{data['type']}")
        return super().load(data, *args, **kwargs)


@dataclass
class LogsCollector(BaseCollector):
    paths: List[str] = field(default_factory=list)
    current_task: TaskLog = field(default_factory=TaskLog)
    indexed_data: LogFilesMapping = field(default_factory=LogFilesMapping)
    match_pattern: MatchingPattern = field(default=MatchingPattern.GLOB)
    full_file: bool = field(default=False)


class LogsCollectorSchema(BaseCollectorSchema):
    paths = fields.List(fields.Str(), required=True)
    current_task = fields.Nested(TaskLogSchema, required=False)
    match_pattern = fields.Enum(MatchingPattern, by_value=True, required=False, missing=MatchingPattern.GLOB, allow_none=True)
    full_file = fields.Bool(required=False, missing=False)

    def load(self, data, *args, **kwargs):
        if "paths" in data:
            match_pattern = data.get("match_pattern", MatchingPattern.GLOB)
            paths = find_paths_by_pattern(data["paths"], match_pattern)
            data["current_task"] = {"paths": paths}
            data["current_task"]['full_file'] = data.get("full_file", False)
            return super().load(data, *args, **kwargs)
        raise ValueError("LogsCollector must have list of paths")

    class Meta:
        unknown = EXCLUDE


@dataclass
class BashCollector(BaseCollector):
    command: str = field(default_factory=str)
    current_task: TaskBash = field(default_factory=TaskBash)
    indexed_data: BashIndex = field(default_factory=BashIndex)


class BashCollectorSchema(BaseCollectorSchema):
    command = fields.Str(required=True)
    current_task = fields.Nested(TaskBashSchema, required=False)

    def load(self, data, *args, **kwargs):
        if 'args' not in data:
            data['args'] = []
        if 'kwargs' not in data:
            data['kwargs'] = {}
        data["current_task"] = {"command": data["command"], "args": data["args"], "kwargs": data["kwargs"]}

        return super().load(data, *args, **kwargs)

    class Meta:
        unknown = EXCLUDE


@dataclass
class BashScriptCollector(BaseCollector):
    script_path: str = field(default_factory=str)
    args: List[str] = field(default_factory=list)
    full_file: bool = field(default=False)


class BashScriptCollectorSchema(BaseCollectorSchema):
    script_path = fields.Str(required=True)
    args = fields.List(fields.Str(), required=False)
    full_file = fields.Bool(required=False, missing=False)

    class Meta:
        unknown = EXCLUDE


@dataclass
class CustomScriptCollector(BaseCollector):
    interpreter_path: str = field(default_factory=str)
    script_path: str = field(default_factory=str)
    args: List[str] = field(default_factory=list)


class CustomScriptCollectorSchema(BaseCollectorSchema):
    interpreter_path = fields.Str(required=True)
    script_path = fields.Str(required=True)
    args = fields.List(fields.Str(), required=False)

    class Meta:
        unknown = EXCLUDE


def ensure_dict(data) -> dict:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid data: {data}")
    return data


def create_collector_instance(collector: dict) -> BaseCollector:
    match CollectorType(collector["type"]):
        case CollectorType.LOGS:
            validated_data = LogsCollectorSchema().load(collector)
            return LogsCollector(**ensure_dict(validated_data))
        case CollectorType.BASH:
            validated_data = BashCollectorSchema().load(collector)
            return BashCollector(**ensure_dict(validated_data))
        case CollectorType.BASH_SCRIPT:
            validated_data = BashScriptCollectorSchema().load(collector)
            return BashScriptCollector(**ensure_dict(validated_data))
        case CollectorType.CUSTOM_SCRIPT:
            validated_data = CustomScriptCollectorSchema().load(collector)
            return CustomScriptCollector(**ensure_dict(validated_data))
        case _:
            raise ValueError(f"Unknown collector type: {collector['type']}")

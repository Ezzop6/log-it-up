from dataclasses import dataclass, field
from typing import Any, Callable, Dict
from enum import Enum
from typing import Union
from marshmallow import Schema, fields, EXCLUDE, validates_schema
from typing import Any, Dict, Union, Callable
from enum import Enum
from config import CollectorType, CollectorFilterType
from datetime import datetime


class TaskExecutionType(Enum):
    INTERVAL = "interval"


class TaskSchema(Schema):
    time_started = fields.DateTime(required=False, missing=datetime.now)
    name = fields.Str(required=True)
    task_id = fields.Int(required=False, missing=0)
    execution_type = TaskExecutionType.INTERVAL
    interval = fields.Raw(required=True)
    task_function = fields.Function(
        required=True, validate=lambda f: callable(f), deserialize=lambda _: _
    )
    args = fields.List(fields.Raw(), required=False, missing=tuple, allow_none=True)
    kwargs = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False, missing=dict, allow_none=True)
    error = fields.Str(required=False, missing="", allow_none=True)
    type = fields.Enum(CollectorType, by_value=True, required=True)
    filter = fields.Enum(CollectorFilterType, by_value=True, required=False, missing=CollectorFilterType.NONE, allow_none=True)
    time_finished = fields.DateTime(required=False, missing=None)
    total_run = fields.Int(default=0)
    current_task = fields.Raw(required=False, missing=None, allow_none=True)
    indexed_data = fields.Raw(required=False, missing=None, allow_none=True)
    task_result = fields.Raw(required=False, missing=None, allow_none=True)

    class Meta:
        unknown = EXCLUDE

    @validates_schema
    def validate_execution_time(self, data, **kwargs):
        interval = data.get("execution_time")
        if isinstance(interval, int):
            if interval == -1:
                raise NotImplementedError("auto exececution not implemented yet")


@dataclass
class Task:
    interval: Union[str, int]
    task_function: Callable[..., None]
    type: CollectorType = CollectorType.NONE
    time_started: datetime = field(default_factory=datetime.now)
    task_id: int = field(default_factory=int)
    name: str = field(default_factory=str)
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    execution_type: TaskExecutionType = TaskExecutionType.INTERVAL
    error: str = field(default_factory=str)
    filter: CollectorFilterType = CollectorFilterType.NONE
    time_finished: Union[datetime, None] = None
    total_run: int = field(default_factory=int)
    current_task: object = field(default=None)
    indexed_data: object = field(default=None)
    task_result: object = field(default=None)

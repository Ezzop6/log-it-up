from dataclasses import dataclass, field
from marshmallow import Schema, fields, EXCLUDE, post_load


@dataclass
class BashIndex:
    index: str = field(default="")

    @post_load
    def make_bash_index(self, data, **kwargs):
        return BashIndex(**data)


class BashIndexSchema(Schema):
    index = fields.Str(required=False, allow_none=True, missing="")

    @post_load
    def make_bash_index(self, data, **kwargs):
        return BashIndex(**data)

    class Meta:
        unknown = EXCLUDE


@dataclass
class TaskBash:
    command: str = field(default_factory=str)
    args: list[str] = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


class TaskBashSchema(Schema):
    command = fields.Str(required=True)
    args = fields.List(fields.Str(), required=False, allow_none=True, missing=[])
    kwargs = fields.Dict(required=False, allow_none=True, missing={})

    @post_load
    def make_task_bash(self, data, **kwargs):
        return TaskBash(**data)

    class Meta:
        unknown = EXCLUDE


@dataclass
class TaskBashResult:
    stdout: str = field(default_factory=str)
    stderr: str = field(default_factory=str)

    @post_load
    def make_task_bash_result(self, data, **kwargs):
        return TaskBashResult(**data)


class TaskBashResultSchema(Schema):
    stdout = fields.Str(required=False, allow_none=True, missing="")
    stderr = fields.Str(required=False, allow_none=True, missing="")

    @post_load
    def make_task_bash_result(self, data, **kwargs):
        return TaskBashResult(**data)

    class Meta:
        unknown = EXCLUDE

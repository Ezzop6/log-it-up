from marshmallow import Schema, fields, EXCLUDE
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    NONE = "NONE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class GlobalConfigSchema(Schema):
    log_level = fields.Enum(LogLevel, by_value=True, required=False)
    ignore_repeated_errors = fields.Bool(required=False, missing=False)
    disabled_collectors_types = fields.List(fields.Str(), required=False, missing=[], allow_none=True)

    class Meta:
        unknown = EXCLUDE


@ dataclass
class GlobalConfig:
    log_level: LogLevel
    ignore_repeated_errors: bool
    disabled_collectors_types: list[str]

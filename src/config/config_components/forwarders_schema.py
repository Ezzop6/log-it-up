from marshmallow import Schema, fields, EXCLUDE, ValidationError, validates_schema
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List
from pathlib import Path
from utils import PATH
from helpers import load_function_from_file


class AuthenticationType(Enum):
    NONE = "none"
    BEARER = "bearer"
    BASIC = "basic"


class ForwarderType(Enum):
    HTTP = "http"
    HTTPS = "https"
    LOCAL_FILE = "local_file"
    LOCAL_DB = "local_db"


@dataclass
class Authentication:
    type: AuthenticationType
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    def __str__(self):
        return f"{self.type}, {self.token}, {self.username}, {self.password}"


class AuthenticationSchema(Schema):
    type = fields.Enum(AuthenticationType, by_value=True, required=True)
    token = fields.Str(required=False)
    username = fields.Str(required=False)
    password = fields.Str(required=False)

    class Meta:
        unknown = EXCLUDE


@dataclass
class Forwarder:
    type: ForwarderType
    batch_size: int
    payload_size: int
    url: Optional[str] = None
    authentication: Optional[Authentication] = None
    headers: Optional[Dict[str, str]] = field(default_factory=dict)
    params: Optional[Dict[str, str]] = field(default_factory=dict)
    path: Optional[str] = None
    data_formatter: Path = PATH.DATA_FORMATTERS / "default_data_formatter.py"
    environment_details: Dict = field(default_factory=dict)
    system_details: Dict = field(default_factory=dict)

    def __str__(self):
        return f"{self.type}, {self.url}, {self.authentication}, {self.headers}, {self.params}"


class ForwarderSchema(Schema):
    batch_size = fields.Int(required=False, allow_none=True, missing=1)
    payload_size = fields.Int(required=False, allow_none=True, missing=1_000_000)
    type = fields.Enum(ForwarderType, by_value=True, required=True)
    url = fields.URL(validates_schema=True, required=False)
    authentication = fields.Nested(AuthenticationSchema, required=False)
    headers = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)
    params = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)
    path = fields.Str(validates_schema=True, required=False)
    data_formatter = fields.Str(validates_schema=True, required=False)
    environment_details = fields.Dict(validates_schema=True, required=False)
    system_details = fields.Dict(validates_schema=True, required=False)

    @validates_schema
    def validate_http_collector(self, data, **kwargs):
        if data['type'] in [ForwarderType.HTTP, ForwarderType.HTTPS]:
            if 'url' not in data:
                raise ValidationError('url parameter is required for http collector')
            self.check_formatter_dir(data)
            self.get_environment_details(data)
            self.get_system_details(data)
            data['data_formatter'] = load_function_from_file(data['data_formatter'], "data_formatter")

    @validates_schema
    def validate_bash_collector(self, data, **kwargs):
        if data['type'] == ForwarderType.LOCAL_FILE and 'path' not in data:
            raise ValidationError('path parameter is required for local file collector')

    def get_system_details(self, data):
        if 'system_details' not in data:
            script_file = load_function_from_file(PATH.UTILS / 'system_details.py', "system_details")
            data['system_details'] = script_file()
        if 'script' in data['system_details']:
            script_file = PATH.get_absolute_path(data['system_details']['script'])
            system_details = load_function_from_file(script_file, "system_details")
            data['system_details'] = system_details()
        assert isinstance(data['system_details'], dict), "system_details must be a dictionary"

    def get_environment_details(self, data):
        if 'environment_details' not in data:
            data['environment_details'] = {}
        if data['environment_details']:
            assert isinstance(data['environment_details'], dict), "environment_details must be a dictionary"

    def check_formatter_dir(self, data):
        if 'data_formatter' not in data:
            data['data_formatter'] = PATH.DATA_FORMATTERS / "default_data_formatter.py"
            return data
        data['data_formatter'] = PATH.get_absolute_path(data['data_formatter'])
        return data

    class Meta:
        unknown = EXCLUDE


@dataclass
class Forwarders:
    forwarder: List[Forwarder]

    def __str__(self):
        return "".join([f"{forwarder}\n" for forwarder in self.forwarder])


class ForwardersSchema(Schema):
    forwarders = fields.List(fields.Nested(ForwarderSchema), required=True)

    class Meta:
        unknown = EXCLUDE

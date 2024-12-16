from .base_model import BaseModel
from datetime import datetime
import uuid
from task_manager.task_components import Task
from config.config_components.logs_collector_schema import LogFileIndex, LogFilesMapping, TaskLog

from peewee import ( # type: ignore
    CharField,
    ForeignKeyField,
    TextField,
    IntegerField,
    DateTimeField,
    UUIDField,
    FloatField
)


class LogCollectorModel(BaseModel):
    id = CharField(primary_key=True, unique=True)
    name = CharField()
    type = CharField()


class PathModel(BaseModel):
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    collector = ForeignKeyField(LogCollectorModel, backref='paths', on_delete='CASCADE')
    path = CharField()
    path_index = IntegerField(default=0)
    last_run = DateTimeField(default=datetime.now)
    total_runs = IntegerField(default=0)
    inode = IntegerField()
    size = IntegerField()
    last_modified = FloatField()

    def update_index(self, data: LogFileIndex) -> None:
        self.path_index = data.index
        self.inode = data.inode
        self.size = data.size
        self.last_modified = data.last_modified
        self.total_runs += 1 # type: ignore
        self.save()


class LogLineModel(BaseModel):
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    collector = ForeignKeyField(LogCollectorModel, backref='log_lines', on_delete='CASCADE')
    path = ForeignKeyField(PathModel, backref='log_lines', on_delete='CASCADE')
    message = TextField()

from task_manager.task_components import Task
from config.config_components import BashIndex, TaskBashResult
from .base_model import BaseModel
from datetime import datetime
import uuid
from peewee import ( # type: ignore
    CharField,
    ForeignKeyField,
    TextField,
    DateTimeField,
    UUIDField,
    IntegerField
)


class BashCollectorModel(BaseModel):
    id = CharField(primary_key=True, unique=True)
    name = CharField()
    type = CharField()


class BashTaskModel(BaseModel):
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    collector = ForeignKeyField(BashCollectorModel, backref='tasks', on_delete='CASCADE')
    stdout_count = IntegerField(default=0)
    stderr_count = IntegerField(default=0)
    task = CharField()
    task_index = CharField(default='string')
    last_run = DateTimeField(default=datetime.now)

    def update_index(self, task: Task) -> None:
        if not isinstance(task.indexed_data, BashIndex):
            raise ValueError(f"Task {task.task_id} does not have indexed data.")
        if not isinstance(task.task_result, TaskBashResult):
            raise ValueError(f"Task {task.task_id} does not have a result.")
        if task.task_result.stdout:
            self.stdout_count = self.stdout_count + 1 # type: ignore
        if task.task_result.stderr:
            self.stderr_count = self.stderr_count + 1 # type: ignore
        self.task_index = task.indexed_data.index
        self.last_run = datetime.now()
        self.save()


class BashResultModel(BaseModel):
    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    collector = ForeignKeyField(BashCollectorModel, backref='results', on_delete='CASCADE')
    task = ForeignKeyField(BashTaskModel, backref='results', on_delete='CASCADE')
    stdout = TextField()
    stderr = TextField()

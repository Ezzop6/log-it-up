from .base_forwarder import BaseForwarder
from task_manager.task_components import Task
from utils import Singleton
from database import Database
from config import CollectorType


class LocalDBForwarder(BaseForwarder, Singleton):
    def __init__(self, *args, **kwargs) -> None:
        if not hasattr(self, '_initialized'):
            self.db = Database()
            self._initialized = True

    def transmit_data(self, task: Task):
        match task.type:
            case CollectorType.LOGS: self.db.add_log_line(task)
            case CollectorType.BASH: self.db.record_bash_result(task)
            case _: raise NotImplementedError(f"Collector type {task.type} not implemented")

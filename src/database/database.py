from .models import DB
from task_manager.task_components import Task
from .models import *
from config.config_components import CollectorType


class Database:
    def __init__(self):
        self.db = DB
        self.initialize_database()

    def initialize_database(self):
        with self.db:
            self.db.create_tables([
                LogCollectorModel,
                PathModel,
                LogLineModel,
                BashCollectorModel,
                BashTaskModel,
                BashResultModel
            ], safe=True)

    def get_indexes(self, task: Task):
        match task.type:
            case CollectorType.LOGS: return self.get_log_indexes(task)
            case CollectorType.BASH: return self.get_bash_indexes(task)
            case _: raise ValueError(f"Unknown type: {task.type}")

    def get_bash_indexes(self, task: Task):
        from .business_logic.bash_operations import get_bash_indexes
        return get_bash_indexes(task)

    def get_log_indexes(self, task: Task):
        from .business_logic.logs_operations import get_log_indexes
        return get_log_indexes(task)

    def add_log_line(self, task: Task):
        from .business_logic.logs_operations import add_log_line
        add_log_line(task)

    def record_bash_result(self, task: Task):
        from .business_logic.bash_operations import record_bash_result
        record_bash_result(task)

    def get_collectors_info(self, type: CollectorType):
        with self.db:
            match type:
                case CollectorType.LOGS: return LogCollectorModel.select()
                case CollectorType.BASH: return BashCollectorModel.select()
                case _: raise ValueError(f"Unknown type: {type}")

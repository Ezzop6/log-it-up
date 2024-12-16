from config import CONFIG
import threading
# from zodb_db import ZODBServer
import time
from .task_components import Task, TaskExecutionType, TaskSchema
from collectors import COLLECTOR_LOADER
from forwarders import FORWARDER
import schedule # type: ignore
from threading import Lock
from utils.logger import AppLogger, logging
from utils import Singleton


class TaskManager(Singleton):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.scheduler = schedule.Scheduler()
            self.tasks = []
            self.active_tasks = []
            self.lock = Lock()
            self.logger = AppLogger()
            self.db = CONFIG.DB
            self._initialized = True

    def generate_task_dict(self, collector) -> dict: # TODO: remove this after refactoring collectors
        return dict(
            name=collector.name,
            type=collector.type,
            task_function=COLLECTOR_LOADER.load(collector.type),
            interval=collector.send_interval,
            args=getattr(collector, "args", tuple()),
            kwargs=collector.__dict__,
            task_id=collector.id,
            filter=collector.filter,
            current_task=collector.current_task,
        )

    def load_tasks(self):
        collectors = CONFIG.collectors
        for collector in collectors:
            validated_task = TaskSchema().load(self.generate_task_dict(collector))
            self.tasks.append(validated_task)
        for task in self.tasks:
            self.schedule_task(Task(**task))

    def schedule_task(self, task: Task):
        match task.execution_type:
            case TaskExecutionType.INTERVAL: self.interval_task(task)
            case _:
                raise ValueError(f"Unknown execution_type: {task.execution_type}")

    def interval_task(self, task: Task):
        if not isinstance(task.interval, int):
            raise ValueError(f"Interval must be of type int, got {type(task.interval)}")
        self.scheduler.every(task.interval).seconds.do(self.run_task_in_thread, task)

    def run_task_in_thread(self, task: Task):
        def task_wrapper():
            try:
                with self.lock:
                    task.indexed_data = self.db.get_indexes(task)
                    task.task_function(task)
            except KeyboardInterrupt:
                self.exit()
            except Exception as e:
                self.logger.record_log_entry(
                    msg=f"Task {task.name} failed: {e}",
                    level=logging.ERROR,
                )
            finally:
                with self.lock:
                    FORWARDER.transmit_task(task)
                    self.active_tasks.remove(threading.current_thread())

        thread = threading.Thread(target=task_wrapper)
        self.active_tasks.append(thread)
        thread.start()

    def exit(self):
        self.scheduler.clear()
        for thread in self.active_tasks:
            thread.join()
        # self.zodb_server.close_connection()
        self.scheduler.clear()
        exit(0)

    def start(self):
        try:
            while True:
                self.scheduler.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            self.exit()

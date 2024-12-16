from abc import ABC, abstractmethod
from task_manager.task_components import Task


class BaseForwarder(ABC):
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True

    @abstractmethod
    def transmit_data(self, task: Task):
        pass

from .base_forwarder import BaseForwarder
from task_manager.task_components import Task


class LocalFileForwarder(BaseForwarder):
    def __init__(self, **args) -> None:
        raise NotImplementedError("LocalForwarder is not implemented yet.")

    def transmit_data(self, task: Task):
        raise NotImplementedError("LocalForwarder is not implemented yet.")

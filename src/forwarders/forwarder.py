from config import CONFIG, ForwarderType
from utils import Singleton
from .forwarder_component import HttpForwarder, LocalFileForwarder, LocalDBForwarder
from utils.logger import AppLogger, logging
from task_manager.task_components import Task


class Forwarder(Singleton):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.logger = AppLogger()
            self.forwarders = []
            self.load_forwarders()
            self._initialized = True

    def load_forwarders(self):
        for forwarder in CONFIG.forwarders:
            try:
                match forwarder.type:
                    case ForwarderType.HTTP: self.forwarders.append(HttpForwarder(**forwarder.__dict__))
                    case ForwarderType.HTTPS: self.forwarders.append(HttpForwarder(**forwarder.__dict__))
                    case ForwarderType.LOCAL_FILE: self.forwarders.append(LocalFileForwarder(**forwarder.__dict__))
                    case ForwarderType.LOCAL_DB: self.forwarders.append(LocalDBForwarder(**forwarder.__dict__))
                    case _: raise ValueError(f"Unknown forwarder type: {forwarder.type}")

            except Exception as e:
                self.logger.record_log_entry(f"Error loading forwarder: {e}", level=logging.ERROR)

    def transmit_task(self, task: Task):
        for forwarder in self.forwarders:
            forwarder.transmit_data(task)


FORWARDER = Forwarder()

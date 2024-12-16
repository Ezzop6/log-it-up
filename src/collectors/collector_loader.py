from utils import Singleton, PATH
from config import CollectorType
import importlib.util
import re
from typing import Callable, Optional


class CollectorLoader(Singleton):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.collector_files = PATH.get_collectors()
            self._initialized = True

    def handle_collector_path(self, collector_type: CollectorType) -> Optional[Callable]:
        search = re.compile(collector_type.value)
        for path in self.collector_files:
            if search.search(str(path)):
                spec = importlib.util.spec_from_file_location("collector", path)

                if not spec or not spec.loader:
                    raise ImportError(f"Could not load module from path: {path}")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                function_name = "handle_data_collection"
                if hasattr(module, function_name):
                    return getattr(module, function_name)

                raise AttributeError(f"Module {path} does not have function {function_name}")
        return None

    def load(self, collector_type: CollectorType) -> Callable:
        collector_function = self.handle_collector_path(collector_type)
        if not collector_function:
            raise ValueError(f"Collector of type '{collector_type}' not found.")
        return collector_function


COLLECTOR_LOADER = CollectorLoader()

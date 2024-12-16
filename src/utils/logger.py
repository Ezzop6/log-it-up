import logging
import os
from functools import wraps
import inspect
from .project_paths import PATH
from datetime import datetime
from utils import Singleton
import yaml # type: ignore
from typing import List
APP_NAME = "Log-It-Up"


def log_record(*args, **kwargs):
    return LOGGER.record_log_entry(*args, **kwargs)


def log_record_context(level=logging.INFO):
    return LOGGER.log_with_context(level)


class AppLogger(Singleton):
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.start_day = self.today()
            self._logger = None
            self.ignore_repeated_errors = False
            self.repeated_errors: List[str] = []
            self.setup_logger()
            self._initialized = True

    def today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def check_day(self):
        if self.start_day != self.today():
            self.start_day = self.today()
            self.setup_logger()

    def get_log_level(self):
        config = yaml.safe_load(open(PATH.CFG, "r"))
        self.log_level = config['global_config']['log_level']
        self.ignore_repeated_errors = config['global_config'].get('ignore_repeated_errors', False)
        return self.log_level

    def setup_logger(self):
        if self._logger:
            while self._logger.hasHandlers():
                self._logger.removeHandler(self._logger.handlers[0])

        self._logger = logging.getLogger(APP_NAME)
        self._logger.setLevel(self.get_log_level())

        self._logger.propagate = False

        log_file = f'{PATH.LOGS}/{APP_NAME}-{self.start_day}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - [%(caller_filename)s:%(caller_lineno)d] %(caller_funcname)s'
        ))
        self._logger.addHandler(file_handler)

    def record_log_entry(self, msg: str, level: int = logging.DEBUG, context: str = ''):
        self.check_day()
        if self.ignore_repeated_errors and msg in self.repeated_errors:
            return
        self.repeated_errors.append(msg)

        stack = inspect.stack()
        caller_frame = None
        for frame in stack:
            if "logger.py" not in frame.filename:
                caller_frame = frame
                break

        if caller_frame:
            filename = os.path.abspath(caller_frame.filename)
            lineno = caller_frame.lineno
            func_name = caller_frame.function
            context = f"[{filename}:{lineno}] {func_name}"
        else:
            context = "[unknown file:0] unknown_function"

        full_message = f"{msg} {context}".strip()

        extra = {'caller_filename': filename, 'caller_lineno': lineno, 'caller_funcname': func_name}
        self._logger.log(level, full_message, extra=extra)

    def log_with_context(self, level=logging.DEBUG):
        """
        Decorator that logs the entry and exit of a function with the given level.
        :param level: logging enum level
        """
        if not isinstance(level, int):
            raise TypeError(f"Log level must be an integer, got {type(level)}")

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                stack = inspect.stack()
                caller_frame = stack[1]

                filename = os.path.basename(caller_frame.filename)
                lineno = caller_frame.lineno
                func_name = func.__name__

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                parameters = ", ".join(args_repr + kwargs_repr)

                context = f"[{filename}:{lineno}] {func_name}({parameters})"

                self.record_log_entry(f"Entering {func_name} with args: {parameters}", level, context)
                try:
                    result = func(*args, **kwargs)
                    self.record_log_entry(f"Exiting {func_name} with result: {result!r}", level, context)
                    return result
                except Exception as e:
                    self.record_log_entry(f"Exception in {func_name}: {e}", logging.ERROR, context)
                    raise
            return wrapper
        return decorator


LOGGER = AppLogger()

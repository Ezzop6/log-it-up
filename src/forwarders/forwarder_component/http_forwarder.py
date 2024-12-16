from pprint import pprint
import requests # type: ignore
import json
from .base_forwarder import BaseForwarder
from task_manager.task_components import Task
from utils.logger import AppLogger, logging
from typing import Callable
DEFAULT_HEADERS = {"Content-Type": "application/json"}


class HttpForwarder(BaseForwarder):
    def __init__(self, **kwargs):
        self.logger = AppLogger()
        self.url = kwargs.get("url", "")
        self.headers = kwargs.get("headers", DEFAULT_HEADERS)
        self.environment_details = kwargs.get("environment_details")
        self.data_formatter: Callable = kwargs.get("data_formatter")
        self.batch_size = kwargs.get("batch_size", 0)
        self.payload_size = kwargs.get("payload_size", 0)
        self.system_details = kwargs.get("system_details")
        if self.batch_size == 0 or self.payload_size == 0:
            raise ValueError("batch_size and payload_size must be set")

    def transmit_data(self, task: Task):
        formatted_data = self.data_formatter(task, self.system_details, self.environment_details)
        self.send_data(formatted_data)

    def send_data(self, formatted_data):
        if len(formatted_data) == 1:
            response = requests.post(self.url, json=formatted_data, headers=self.headers)
            if response.status_code != 200:
                self.logger.record_log_entry(
                    f"{response.status_code} sending data to {self.url}: {response.text}",
                    level=logging.ERROR
                )
        else:
            self.send_data_in_batches(formatted_data)

    def send_data_in_batches(self, formatted_data):
        for i in range(0, len(formatted_data), self.batch_size):
            batch = formatted_data[i:i + self.batch_size]

            # Check if the payload is too large
            payload = json.dumps(batch)
            if len(payload.encode('utf-8')) > self.payload_size:
                # If the payload is too large, remove the last element and try again
                while len(payload.encode('utf-8')) > self.payload_size:
                    batch = batch[:-1]
                    payload = json.dumps(batch)
            try:
                response = requests.post(self.url, json=batch, headers=self.headers)
                if response.status_code != 200:
                    self.logger.record_log_entry(
                        f"{response.status_code} sending data to {self.url}: {response.text}",
                        level=logging.ERROR
                    )
            except Exception as e:
                self.logger.record_log_entry(
                    f"Error sending batch: {str(e)}",
                    level=logging.ERROR
                )

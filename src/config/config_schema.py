from utils import PATH, Singleton
import yaml # type: ignore
from typing import List
from database import Database
from .config_components import (
    GlobalConfigSchema,
    ForwardersSchema,
    GlobalConfig,
    Forwarders,
    Forwarder,
    BaseCollector,
    create_collector_instance
)


class ConfigSchema(Singleton):
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.DB = Database()
            self.cfg = self.load_config_file()
            self.global_config = self.load_global_config(self.cfg["global_config"], GlobalConfigSchema)
            self.forwarders = self.load_forwarders(self.cfg["forwarders"], ForwardersSchema).forwarder
            self.collector_categories = list(set([collector["type"] for collector in self.cfg["collectors"]]))
            self.collectors = self.load_collectors(self.cfg["collectors"])
            self._initialized = True

    def load_config_file(self) -> dict:
        with open(PATH.CFG, "r") as file:
            data = yaml.safe_load(file)
        return data

    def load_global_config(self, data: dict, schema) -> GlobalConfig:
        validated_data = schema().load(data)
        return GlobalConfig(**validated_data)

    def load_forwarders(self, data: list, schema) -> Forwarders:
        validated_data = schema().load({"forwarders": data})
        forwarders = [Forwarder(**item) for item in validated_data["forwarders"]]
        return Forwarders(forwarders)

    def load_collectors(self, data: List[dict]) -> List[BaseCollector]:
        collectors: List[BaseCollector] = []
        for collector in data:
            collector_instance = create_collector_instance(collector)
            if collector_instance.type.value in self.global_config.disabled_collectors_types:
                continue
            if collector_instance.id in [c.id for c in collectors]:
                raise ValueError(f"Duplicate collector id: {collector_instance.name} - Name must be unique.")
            collectors.append(collector_instance)
        return collectors


CONFIG = ConfigSchema()

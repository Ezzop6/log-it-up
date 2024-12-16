from .singleton import Singleton
from pathlib import Path
from typing import List, Union


class ProjectPaths(Singleton):
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.ROOT = Path(__file__).parent.parent.parent
            self.SRC = self.ROOT / "src"
            self.LOGS = self.ROOT / "logs"
            self.CFG = self.ROOT / "config.yaml"
            self.COLLECTORS_PATH = self.SRC / "collectors/collector"
            self.DATABASE_DATA_DIR = self.SRC / "database" / "data"
            self.DATABASE_FILE = self.DATABASE_DATA_DIR / "database.db"
            self.DATA_FORMATTERS = self.SRC / "data_formatters"
            self.UTILS = self.SRC / "utils"
            self.validate()
            self._initialized = True

    def validate(self) -> None:
        assert self.ROOT.exists()
        assert self.SRC.exists()
        assert self.LOGS.exists()
        assert self.CFG.exists(), "Copy config-example.yaml to config.yaml and fill in the values."
        assert self.DATABASE_DATA_DIR.exists()
        assert self.COLLECTORS_PATH.exists()

    def get_collectors(self) -> List[Path]:
        return [file for file in self.COLLECTORS_PATH.iterdir() if file.is_file()]

    def get_absolute_path(self, file_path: Union[str, Path]) -> Path:
        file_path = Path(file_path)
        if file_path.is_absolute() and file_path.exists():
            return file_path

        searchable_paths = [
            self.DATA_FORMATTERS,
        ]

        for path in searchable_paths:
            if (path / file_path).exists():
                return path / file_path

        raise FileNotFoundError(f"File {file_path} not found")


PATH = ProjectPaths()

import os
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from config.config_components.logs_collector_schema import LogFileIndex


class FileStatus(Enum):
    UNCHANGED = 0
    UPDATED = 1
    TRUNCATED = 2
    DELETED = 3
    REPLACED = 4


@dataclass
class FileMetadata:
    inode: int
    size: int
    last_modified: float
    lines: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileMetadata):
            raise ValueError(f"Cannot compare FileMetadata with {type(other)}")
        return (
            self.inode == other.inode
            and self.size == other.size
            and self.last_modified == other.last_modified
        )

    def __hash__(self) -> int:
        return hash((self.inode, self.size, self.last_modified))


class FileWatcher:
    def _get_metadata(self, path: Path | str) -> FileMetadata:
        stat = os.stat(path)
        return FileMetadata(
            inode=stat.st_ino,
            size=stat.st_size,
            last_modified=stat.st_mtime,
            lines=self.get_line_count(path),
        )

    def get_metadata(self, path: Path | str) -> LogFileIndex:
        metadata = self._get_metadata(path)
        if metadata is None:
            raise FileNotFoundError(f"File {path} does not exist.")
        return LogFileIndex(
            path=str(path),
            index=self.get_line_count(path),
            inode=metadata.inode,
            size=metadata.size,
            last_modified=metadata.last_modified,
        )

    def check_file_status(self, indexed_file: LogFileIndex, tracked_file_path: Path | str) -> FileStatus:
        current_metadata = self._get_metadata(tracked_file_path)

        if current_metadata is None:
            return FileStatus.DELETED

        if current_metadata.inode != indexed_file.inode:
            return FileStatus.REPLACED

        if current_metadata.size > indexed_file.size:
            return FileStatus.UPDATED

        elif current_metadata.size < indexed_file.size:
            return FileStatus.TRUNCATED

        elif current_metadata.last_modified != indexed_file.last_modified:
            return FileStatus.UPDATED

        return FileStatus.UNCHANGED

    def is_file_updated(self, indexed_file: LogFileIndex, tracked_file_path: Path | str) -> bool:
        status = self.check_file_status(indexed_file, tracked_file_path)
        return status in {FileStatus.UPDATED, FileStatus.REPLACED, FileStatus.TRUNCATED}

    def get_line_count(self, path: Path | str) -> int:
        with open(path) as file:
            return sum(1 for _ in file)

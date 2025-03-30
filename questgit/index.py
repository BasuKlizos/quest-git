import os
import zlib
from typing import Dict, Optional

from utils.logger_utils import LoggerUtil
from utils.file_utils import FileHandler
from utils.constants import INDEX_FILE
from questgit.objects import ObjectStore

logger = LoggerUtil.setup_logger(__name__)


class Index:
    def __init__(self):
        self.entries: Dict[str, str] = {}  # filepath, hash
        self.load()

    def load(self):
        self.entries = {}

        if not os.path.exists(INDEX_FILE):
            return

        compressed_content = FileHandler.read_binary(INDEX_FILE)
        if not compressed_content:
            return

        try:
            data = zlib.decompress(compressed_content).decode("utf-8")
            for line in data.splitlines():
                if line.strip():
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        hash_val, file_path = parts
                        self.entries[file_path] = hash_val
        except zlib.error as e:
            logger.error(f"Index file corruption: {e}")
            self.entries = {}

    def save(self):
        data = "\n".join(
            f"{hash_val} {file_path}" for file_path, hash_val in self.entries.items()
        )

        compressed_content = zlib.compress(data.encode("utf-8"))
        FileHandler.write_binary(INDEX_FILE, compressed_content)
        logger.info("Index save successfully")

    def add_entry(self, filepath: str, hash_val: str):
        self.entries[filepath] = hash_val

    def get_entry(self, filepath: str) -> Optional[str]:
        return self.entries.get(filepath)

    def remove_entry(self, filepath: str):
        if filepath in self.entries:
            del self.entries[filepath]

    def get_file_contents(self, filepath: str) -> Optional[str]:
        blob_hash = self.get_entry(filepath)

        return ObjectStore.read_blob(blob_hash) if blob_hash else None

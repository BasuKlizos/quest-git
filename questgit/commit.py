import os
import zlib
from datetime import datetime
from typing import Optional
from utils.file_utils import FileHandler
from utils.hash_utils import HashCalculate
from utils.constants import (
    OBJECTS_DIR,
    MASTER_FILE,
    BLOB_DIR_LEN,
    BLOB_HASH_LEN,
    GIT_DIR,
)
from utils.logger_utils import LoggerUtil
from .objects import ObjectStore
from .index import Index
from .config import Config

logger = LoggerUtil.setup_logger(__name__)


class Commit:
    @staticmethod
    def _store_object(content: str) -> str:
        obj_hash = HashCalculate.calculate_sha1(content)
        obj_dir = os.path.join(OBJECTS_DIR, obj_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, obj_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        FileHandler.ensure_directory_exists(obj_dir)
        FileHandler.write_binary(obj_path, zlib.compress(content.encode()))
        return obj_hash

    @staticmethod
    def _create_tree_object() -> str:
        tree_entries = []
        for filepath, blob_hash in Index().entries.items():
            filename = os.path.basename(filepath)
            tree_entries.append(f"100644 blob {blob_hash} {filename}")
        return Commit._store_object("\n".join(tree_entries))

    @staticmethod
    def create_commit(message: str) -> Optional[str]:
        try:
            if not Index().entries:
                logger.error("Nothing to commit (index is empty)")
                return None

            config = FileHandler.read_config(Config.CONFIG_PATH)
            author = config.get("user.name", "Anonymous")
            email = config.get("user.email", "Anonymous")

            tree_hash = Commit._create_tree_object()

            parent_hash = None
            if os.path.exists(MASTER_FILE):
                parent_hash = FileHandler.read(MASTER_FILE).strip()

            timestamp = int(datetime.now().timestamp())
            commit_content = (
                f"tree {tree_hash}\n"
                + (f"parent {parent_hash}\n" if parent_hash else "")
                + f"author {author} <{email}> {timestamp}\n"
                + f"committer {author} <{email}> {timestamp}\n\n"
                + f"{message}\n"
            )
            commit_hash = Commit._store_object(commit_content)

            FileHandler.write(MASTER_FILE, commit_hash)
            Index().entries = {}
            Index().save()

            logger.info(f"Created commit {commit_hash[:8]}")
            return commit_hash

        except Exception as e:
            logger.error(f"Commit failed: {str(e)}")
            return None

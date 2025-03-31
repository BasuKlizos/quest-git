import os
import zlib
from datetime import datetime
from typing import Optional, List

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

index = Index()


class Commit:

    IGNORED_DIRS = {
        ".venv",
        "__pycache__",
        ".git",
        GIT_DIR,
        "questgit.egg-info",
        ".idea",
        ".vscode",
    }

    @staticmethod
    def _store_object(content: str) -> str:
        obj_hash = HashCalculate.calculate_sha1(content)
        obj_dir = os.path.join(OBJECTS_DIR, obj_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, obj_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        FileHandler.ensure_directory_exists(obj_dir)
        FileHandler.write_binary(obj_path, zlib.compress(content.encode()))
        return obj_hash

    @staticmethod
    def _create_tree_object(directory: str = ".", ignore_dirs: List[str] = None) -> str:
        if ignore_dirs is None:
            ignore_dirs = Commit.IGNORED_DIRS

        entries = []
        for item in sorted(os.listdir(directory)):
            full_path = os.path.join(directory, item)
            relative_path = os.path.relpath(full_path)

            if os.path.isdir(full_path):
                if item in ignore_dirs:
                    continue

                # Recursively create tree for subdirectory
                subtree_hash = Commit._create_tree_object(full_path)
                entries.append(f"040000 tree {subtree_hash}    {item}")
            else:
                # Create blob for file
                with open(full_path, "rb") as f:
                    content = f.read()
                # content = FileHandler.read_binary(full_path)
                # print("tree===========", content)
                blob_hash = HashCalculate.calculate_sha1(content)
                ObjectStore.store_blob(content)
                entries.append(f"100644 blob {blob_hash}    {item}")

        tree_content = "\n".join(entries)
        tree_hash = HashCalculate.calculate_sha1(tree_content)
        ObjectStore.write_blob(tree_content, obj_type="tree")

        return tree_hash

        # for filepath, blob_hash in index.entries.items():
        #     filename = os.path.basename(filepath)
        #     tree_entries.append(f"100644 blob {blob_hash} {filename}")
        # return Commit._store_object("\n".join(tree_entries))

    @staticmethod
    def create_commit(message: str) -> Optional[str]:
        try:

            if not index.entries:
                logger.error("Nothing to commit (index is empty)")
                return None

            config = FileHandler.read_config(Config.CONFIG_PATH)
            author = config.get("user.name", "Anonymous")
            email = config.get("user.email", "Anonymous")

            tree_hash = Commit._create_tree_object()
            if not tree_hash:
                logger.error("Failed to create tree object")
                return None

            parent_hash = None
            if os.path.exists(MASTER_FILE):
                parent_hash = FileHandler.read(MASTER_FILE).strip()
                if not parent_hash or not ObjectStore.blob_exists(parent_hash):
                    parent_hash = None

            timestamp = int(datetime.now().timestamp())
            commit_content = (
                f"tree {tree_hash}\n"
                + (f"parent {parent_hash}\n" if parent_hash else "")
                + f"author {author} <{email}> {timestamp}\n"
                + f"committer {author} <{email}> {timestamp}\n\n"
                + f"{message}\n"
            )
            # commit_hash = Commit._store_object(commit_content)
            commit_hash = ObjectStore.write_blob(commit_content, "commit")

            FileHandler.write(MASTER_FILE, commit_hash)

            # Only remove if file matches current state
            for file in list(index.entries.keys()):
                current_hash = HashCalculate.calculate_sha1(FileHandler.read(file))
                if current_hash == index.entries[file]:
                    index.remove_entry(file)

            index.save()

            logger.info(f"Created commit {commit_hash[:8]}")
            return commit_hash

        except Exception as e:
            logger.error(f"Commit failed: {str(e)}")
            return None

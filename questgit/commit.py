import os
import zlib
from datetime import datetime
from typing import Optional, List, Dict

from utils.file_utils import FileHandler
from utils.hash_utils import HashCalculate
from utils.constants import (
    OBJECTS_DIR,
    MASTER_FILE,
    BLOB_DIR_LEN,
    BLOB_HASH_LEN,
    GIT_DIR,
    REFS_DIR,
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

        # Process files in the index (already staged files)
        for filepath, blob_hash in list(index.entries.items()):
            try:
                # Verify file still exists
                if not os.path.exists(filepath):
                    logger.warning(f"File not found, removing from index: {filepath}")
                    index.remove_entry(filepath)
                    continue

                # Read file content
                # print("=================read==================")
                content = FileHandler.read(filepath)
                if content is None:
                    continue
                # print("=============", content)

                # Verify content hasn't changed since staging
                current_hash = HashCalculate.calculate_sha1(content)
                if current_hash != blob_hash:
                    # print("=================Hash==================")
                    logger.warning(f"File modified since staging: {filepath}")
                    continue

                # Add to tree entries
                filename = os.path.basename(filepath)
                dirname = os.path.dirname(filepath)
                # print("=========", filename,"\n===========", dirname,"\n==============", directory)

                # Handle nested directory structure
                if dirname and dirname != directory:
                    # This will create subtrees automatically through recursion
                    continue

                entries.append(f"100644 blob {blob_hash}    {filename}")
                # print("=========", entries)

            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")
                continue

        # Process directories (for nested structure)
        for item in sorted(os.listdir(directory)):
            if item in ignore_dirs:
                continue

            full_path = os.path.join(directory, item)
            # print("=====full_path===", full_path)
            # print("=====full_path===", type(full_path))
            if os.path.isdir(full_path):
                # Recursively create subtree
                # print("============", entries)
                try:
                    subtree_hash = Commit._create_tree_object(full_path, ignore_dirs)
                    # print("----------subtree-----------",subtree_hash)
                    entries.append(f"040000 tree {subtree_hash}    {item}")
                except Exception as e:
                    logger.error(f"Error processing directory {full_path}: {e}")
                    print(f"Error processing directory {full_path}: {e}")
                    continue

        # print("=======entries=====", entries)

        if not entries:
            raise ValueError(f"No valid files to commit in {directory}")

        tree_content = "\n".join(entries)
        return ObjectStore.store_tree(tree_content)

    @staticmethod
    def create_commit(message: str) -> Optional[str]:
        try:

            if not index.entries:
                logger.error("Nothing to commit (index is empty)")
                return None

            config = FileHandler.read_config(Config.CONFIG_PATH)
            author = config.get("user.name", "Anonymous")
            email = config.get("user.email", "Anonymous")

            try:
                tree_hash = Commit._create_tree_object()
                # print("======tree_hash===============", tree_hash)
            except ValueError as e:
                logger.error(str(e))
                return None

            parent_hash = None
            if os.path.exists(MASTER_FILE):
                # print("=======master=========", MASTER_FILE)
                parent_hash = FileHandler.read(MASTER_FILE).strip()
                # print("=======parent=========", parent_hash)
                # if not parent_hash or not ObjectStore.blob_exists(parent_hash):
                #     parent_hash = None
            else:
                logger.info("MASTER_FILE not found, treating as first commit.")
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
            # print("==========commit_hash==========", commit_hash)

            # FileHandler.write(MASTER_FILE, commit_hash)
            if commit_hash:
                FileHandler.write(MASTER_FILE, commit_hash)
                logger.info(f"Updated MASTER_FILE with new commit hash: {commit_hash}")
            else:
                logger.error("Commit hash generation failed, MASTER_FILE not updated.")

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

    # For log history
    @staticmethod
    def get_log(ref: str = "master", max_count: int = 10) -> List[Dict]:
        commits = []
        current_hash = Commit._resolve_ref(ref)

        while current_hash and len(commits) < max_count:
            commit = Commit._parse_commit(current_hash)
            if not commit:
                break

            commits.append(commit)
            current_hash = commit.get("parent")

        return commits

    @staticmethod
    def _resolve_ref(ref: str) -> Optional[str]:
        ref_path = os.path.join(REFS_DIR, "heads", ref)
        if os.path.exists(ref_path):
            return FileHandler.read(ref_path).strip()
        return ref if ObjectStore.blob_exists(ref) else None

    @staticmethod
    def _parse_commit(commit_hash: str) -> Optional[Dict]:
        content = ObjectStore.read_blob(commit_hash)
        if not content:
            return None

        commit = {"hash": commit_hash}
        lines = content.split("\n")

        for line in lines:
            if line.startswith("tree "):
                commit["tree"] = line[5:]
            elif line.startswith("parent "):
                commit["parent"] = line[7:]
            elif line.startswith("author "):
                author_parts = line[7:].split()
                commit["author"] = " ".join(author_parts[:-2])
                commit["email"] = author_parts[-2][1:-1]  # Remove <>
                timestamp = int(author_parts[-1])
                commit["date"] = datetime.fromtimestamp(timestamp)
            elif not line and "message" not in commit:
                commit["message"] = "\n".join(lines[lines.index("") + 1:])
                break

        return commit

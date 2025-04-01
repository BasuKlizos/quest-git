import zlib
import os
from typing import Optional, List, Dict

from utils.logger_utils import LoggerUtil
from utils.file_utils import FileHandler
from utils.hash_utils import HashCalculate
from utils.constants import OBJECTS_DIR, BLOB_DIR_LEN, BLOB_HASH_LEN

logger = LoggerUtil.setup_logger(__name__)


class ObjectStore:

    @staticmethod
    def store_blob(filepath: str) -> str:
        content = FileHandler.read(filepath)
        if content is None:
            raise ValueError(f"Could not read file: {filepath}")

        blob_hash = HashCalculate.calculate_sha1(content)
        compressed_content = zlib.compress(content.encode("utf-8"))

        obj_dir = os.path.join(OBJECTS_DIR, blob_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, blob_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        FileHandler.ensure_directory_exists(obj_dir)
        FileHandler.write_binary(obj_path, compressed_content)

        logger.info(f"Stored blob {blob_hash} for {filepath}")
        return blob_hash

    @staticmethod
    def read_blob(blob_hash: str) -> Optional[str]:
        obj_dir = os.path.join(OBJECTS_DIR, blob_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, blob_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        compressed_content = FileHandler.read_binary(obj_path)
        if compressed_content is None:
            logger.error(f"Blob object not found: {blob_hash}")
            return None

        try:
            return zlib.decompress(compressed_content).decode("utf-8")
        except zlib.error as e:
            logger.error(f"Decompossing error for blob {blob_hash}: {e}")
            return None

    @staticmethod
    def write_blob(content: str, obj_type: str = "blob") -> str:
        header = f"{obj_type} {len(content)}\0"
        full_content = header.encode() + content.encode()
        # print("========full_content=========", full_content)

        # Calculate hash and store
        blob_hash = HashCalculate.calculate_sha1(full_content.decode("utf-8"))
        obj_dir = os.path.join(OBJECTS_DIR, blob_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, blob_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        FileHandler.ensure_directory_exists(obj_dir)
        compressed = zlib.compress(full_content)
        FileHandler.write_binary(obj_path, compressed)
        # print("=====blob======",blob_hash)

        return blob_hash

    @staticmethod
    def store_tree(tree_content: str) -> str:
        header = f"tree {len(tree_content)}"
        # print("=========Header======", header)
        full_content = header + tree_content
        # print("======full===", full_content)

        # Calculate hash (needs to be on the encoded bytes)
        full_content_bytes = full_content.encode("utf-8")
        # print("=======full_byte======", full_content_bytes)
        # print("=======full======", type(full_content_bytes))

        tree_hash = HashCalculate.calculate_sha1(full_content_bytes.decode("utf-8"))
        # print("=========tree_hash=====", tree_hash)

        # Prepare storage path
        obj_dir = os.path.join(OBJECTS_DIR, tree_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, tree_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        # Store compressed content
        FileHandler.ensure_directory_exists(obj_dir)
        # print("=============empty==================")
        FileHandler.write_binary(obj_path, zlib.compress(full_content_bytes))

        logger.info(f"Stored tree {tree_hash}")
        # print(f"Stored tree {tree_hash}")
        return tree_hash

    @staticmethod
    def blob_exists(blob_hash: str) -> bool:
        if not blob_hash:
            return False
        obj_dir = os.path.join(OBJECTS_DIR, blob_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, blob_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        return os.path.exists(obj_path)

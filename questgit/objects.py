import zlib
import os
from typing import Optional

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
            return None

        try:
            return zlib.decompress(compressed_content).decode("utf-8")
        except zlib.error as e:
            logger.error(f"Decompossing error for blob {blob_hash}: {e}")
            return None

    @staticmethod
    def blob_exists(blob_hash: str) -> bool:
        obj_dir = os.path.join(OBJECTS_DIR, blob_hash[:BLOB_DIR_LEN])
        obj_path = os.path.join(obj_dir, blob_hash[BLOB_DIR_LEN:BLOB_HASH_LEN])

        return os.path.exists(obj_path)

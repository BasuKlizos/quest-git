import os
from typing import Optional, Dict

from utils.logger_utils import LoggerUtil


logger = LoggerUtil.setup_logger(__name__)


class FileHandler:

    @staticmethod
    def read(filepath: str) -> Optional[str]:
        if not os.path.isfile(filepath):
            logger.warning(f"File not found: {filepath}")
            return None
        # with open(filepath, "r", encoding="utf-8") as f:
        #         # print(".................",f.read())
        #         return f.read()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                # print(".................",f.read())
                return f.read()
        except IOError as e:
            logger.error(f"Error reading file {filepath} : {e}")
            return None

    @staticmethod
    def read_binary(filepath: str) -> Optional[bytes]:
        if not os.path.isfile(filepath):
            logger.warning(f"File not found: {filepath}")
            return None
        try:
            with open(filepath, "rb") as f:
                return f.read()
        except IOError as e:
            logger.error(f"Error reading file {filepath}: {e}")
            return None

    @staticmethod
    def write(filepath: str, content: str):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Successfully worte to file: {filepath}")
        except IOError as e:
            logger.error(f"Error writing to file {filepath}: {e}")

    @staticmethod
    def write_binary(filepath: str, content: bytes):
        try:
            with open(filepath, "wb") as f:
                f.write(content)
            logger.info(f"Successfully worte to file: {filepath}")
        except IOError as e:
            logger.error(f"Error writing to file {filepath}: {e}")

    @staticmethod
    def append(filepath, content):
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(content, "\n")
            logger.info(f"Successfully appended to file: {filepath}")
        except IOError as e:
            logger.error(f"Error appending to file {filepath}: {e}")

    @staticmethod
    def append_binary(filepath: str, content: str):
        try:
            with open(filepath, "ab") as f:
                f.write(content)
            logger.info(f"Successfully appended to file: {filepath}")
        except IOError as e:
            logger.error(f"Error appending to file {filepath}: {e}")
            return None

    @staticmethod
    def ensure_directory_exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
        except OSError as e:
            logger.error(f"Error creating directory {directory}: {e}")

    @staticmethod
    def ensure_filepath_exists(filepath):
        try:
            open(filepath, "a").close()
            logger.info(f"File ensured: {filepath}")
        except IOError as e:
            logger.error(f"Error ensuring file {filepath}: {e}")

    @staticmethod
    def read_config(filepath: str) -> Dict[str, str]:
        content = FileHandler.read(filepath)
        if not content:
            return {}

        config = {}
        for line in content.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
        return config

    @staticmethod
    def write_config(filepath: str, config: Dict[str, str]):
        content = "\n".join(f"{key}={val}" for key, val in config.items())
        FileHandler.write(filepath, content)

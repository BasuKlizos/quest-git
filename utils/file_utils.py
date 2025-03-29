import os
from utils.logger_utils import LoggerUtil


logger = LoggerUtil.setup_logger(__name__)


class FileHandler:

    @staticmethod
    def read(filepath):
        if not os.path.isfile(filepath):
            logger.warning(f"File not found: {filepath}")
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except IOError as e:
            logger.error(f"Error reading file {filepath} : {e}")
            return None

    @staticmethod
    def write(filepath, content):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
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

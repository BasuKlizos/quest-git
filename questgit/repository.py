import os
import shutil
from typing import List

from utils.logger_utils import LoggerUtil
from utils.constants import (
    GIT_DIR,
    INDEX_FILE,
    HEAD_FILE,
    MASTER_FILE,
    REQUIRED_DIRS,
)
from utils.file_utils import FileHandler
from questgit.config import Config

# from pathlib import Path


logger = LoggerUtil.setup_logger(__name__)


class Repository:

    IGNORED_DIRS = {
        ".venv",
        "__pycache__",
        ".git",
        GIT_DIR,
        "questgit.egg-info",
        ".idea",
        ".vscode",
    }

    @classmethod
    def init(cls):

        if Repository.is_initialized():
            logger.error("Error: Repository already initialized.")
            print("\033[91mError: Repository already initialized.\033[0m")
            return

        try:
            # os.makedirs(cls.OBJECTS_DIR, exist_ok=True)
            # os.makedirs(cls.REFS_DIR, exist_ok=True)
            # os.makedirs(cls.HEADS_DIR, exist_ok=True)
            for directory in REQUIRED_DIRS:
                FileHandler.ensure_directory_exists(directory)

            # open(cls.INDEX_FILE, "a").close()
            FileHandler.ensure_filepath_exists(INDEX_FILE)

            # with open(cls.HEAD_FILE, "w") as f_data:
            #     f_data.write("ref: refs/master\n")
            FileHandler.write(HEAD_FILE, "ref: refs/heads/master\n")

            # with open(cls.MASTER_FILE, "w") as m_data:
            #     m_data.write("")
            FileHandler.write(MASTER_FILE, "")

            Config.prompt_setup()

            # os.rename(cls.TEMP_GIT_DIR, cls.GIT_DIR)
            logger.info("Initialized empty questgit repository")
            print("\033[92mInitialized empty questgit repository.\033[0m")

        except (FileExistsError, PermissionError) as fp:
            logger.error(f"File error: {fp}")
            shutil.rmtree(GIT_DIR, ignore_errors=True)
            print("\033[91mError: Failed to initialize repository.\033[0m")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            shutil.rmtree(GIT_DIR, ignore_errors=True)
            print("\033[91mUnexpected error occurred.\033[0m")

    @staticmethod
    def is_initialized() -> bool:
        return os.path.isdir(GIT_DIR)

    @staticmethod
    def get_working_dir() -> str:
        return os.getcwd()

    @staticmethod
    def get_relative_path(filepath: str, working_dir: str) -> str:
        return os.path.relpath(filepath, working_dir)

    @classmethod
    def find_files(cls, path: str = ".", ignore_dirs: List[str] = None) -> List[str]:
        if ignore_dirs is None:
            ignore_dirs = cls.IGNORED_DIRS

        files = []
        for root, dirs, filenames in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for filename in filenames:
                filepath = os.path.join(root, filename)
                files.append(filepath)

        return files

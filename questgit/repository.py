import os
import shutil

from utils.logger_utils import LoggerUtil
from utils.constants import (
    GIT_DIR,
    INDEX_FILE,
    HEAD_FILE,
    MASTER_FILE,
    REQUIRED_DIRS,
)
from utils.file_utils import FileHandler

# from pathlib import Path


logger = LoggerUtil.setup_logger(__name__)


class Repository:

    # GIT_DIR = Path(".questgit")
    # OBJECTS_DIR = GIT_DIR / "objects"
    # REFS_DIR = GIT_DIR / "refs"
    # INDEX_FILE = GIT_DIR / "index"
    # HEAD_FILE = REFS_DIR / "HEAD"
    # MASTER_FILE = REFS_DIR / "master"

    # @classmethod
    # def init(cls):

    #     cls.OBJECTS_DIR.mkdir(parents=True, exist_ok=True)
    #     cls.REFS_DIR.mkdir(parents=True, exist_ok=True)
    #     cls.INDEX_FILE.touch()

    #     cls.HEAD_FILE.write_text("ref: refs/master\n")
    # GIT_DIR = ".questgit"
    # TEMP_GIT_DIR = ".temp-questgit"
    # OBJECTS_DIR = os.path.join(TEMP_GIT_DIR, "objects")
    # REFS_DIR = os.path.join(TEMP_GIT_DIR, "refs")
    # HEADS_DIR = os.path.join(REFS_DIR, "heads")
    # INDEX_FILE = os.path.join(TEMP_GIT_DIR, "index")
    # HEAD_FILE = os.path.join(TEMP_GIT_DIR, "HEAD")
    # MASTER_FILE = os.path.join(HEADS_DIR, "master")

    @classmethod
    def init(cls):
        try:
            if os.path.exists(GIT_DIR):
                logger.error("Error: Repository already initialized.")
                print("\033[91mError: Repository already initialized.\033[0m")
                return

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

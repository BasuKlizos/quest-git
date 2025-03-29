import os
import shutil

# from pathlib import Path


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
    GIT_DIR = ".questgit"
    TEMP_GIT_DIR = ".temp-questgit"
    OBJECTS_DIR = os.path.join(TEMP_GIT_DIR, "objects")
    REFS_DIR = os.path.join(TEMP_GIT_DIR, "refs")
    # HEADS_DIR = os.path.join(REFS_DIR, "heads")
    INDEX_FILE = os.path.join(TEMP_GIT_DIR, "index")
    HEAD_FILE = os.path.join(TEMP_GIT_DIR, "HEAD")
    MASTER_FILE = os.path.join(TEMP_GIT_DIR, "master")

    @classmethod
    def init(cls):
        try:
            if os.path.exists(cls.GIT_DIR):
                print("Error: Repository already initialized.")
                return

            os.makedirs(cls.OBJECTS_DIR, exist_ok=True)
            os.makedirs(cls.REFS_DIR, exist_ok=True)

            open(cls.INDEX_FILE, "a").close()

            with open(cls.HEAD_FILE, "w") as f_data:
                f_data.write("ref: refs/master\n")

            with open(cls.MASTER_FILE, "w") as m_data:
                m_data.write("")

            os.rename(cls.TEMP_GIT_DIR, cls.GIT_DIR)
            print("Initialized empty questgit repository")

        except (FileExistsError,  PermissionError) as fp:
            print(f"File exist error: {fp}")
            shutil.rmtree(cls.TEMP_GIT_DIR, ignore_errors=True)
        except Exception as e:
            print(f"Unexpected error: {e}")
            shutil.rmtree(cls.TEMP_GIT_DIR, ignore_errors=True)

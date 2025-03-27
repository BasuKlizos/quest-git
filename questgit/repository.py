import os

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
    OBJECTS_DIR = os.path.join(GIT_DIR, "objects")
    REFS_DIR = os.path.join(GIT_DIR, "refs")
    INDEX_FILE = os.path.join(GIT_DIR, "index")
    HEAD_FILE = os.path.join(REFS_DIR, "HEAD")
    MASTER_FILE = os.path.join(REFS_DIR, "master")

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

            print("Initialized empty questgit repository")
        except FileExistsError as fe:
            print(f"File exist error: {fe}")
        except PermissionError as p:
            print(f"Error: Permission denied. Try running as administrator.\nerror:{p}")
        except Exception as e:
            print("Unexpected error: {e}")

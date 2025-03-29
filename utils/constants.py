import os

GIT_DIR = ".questgit"
OBJECTS_DIR = os.path.join(GIT_DIR, "objects")
REFS_DIR = os.path.join(GIT_DIR, "refs")
INDEX_FILE = os.path.join(GIT_DIR, "index")
HEADS_DIR = os.path.join(REFS_DIR, "heads")
HEAD_FILE = os.path.join(GIT_DIR, "HEAD")
MASTER_FILE = os.path.join(HEADS_DIR, "master")

REQUIRED_DIRS = [OBJECTS_DIR, REFS_DIR, HEADS_DIR]

import sys
import os

from questgit.repository import Repository
from questgit.index import Index
from utils.file_utils import FileHandler
from questgit.objects import ObjectStore
from utils.hash_utils import HashCalculate
from utils.logger_utils import LoggerUtil

logger = LoggerUtil.setup_logger(__name__)


class CLIHandler:
    def __init__(self):
        self.commands = {
            "init": self.init_repo,
            "add": self.add_files,
            "status": self.show_status,
        }

    def run(self):
        if len(sys.argv) < 2:
            self.show_usage()
            return

        command = sys.argv[1]
        action = self.commands.get(command)

        if action:
            action()
        else:
            print(f"Unknown command: {command}")
            self.show_usage()

    def init_repo(self):
        Repository.init()

    def add_files(self):
        if not Repository.is_initialized():
            print("Not a questgit repository")
            return

        if len(sys.argv) < 3:
            print("Usage: questgit add <file1> [<file2> ...]")
            return

        files_to_add = sys.argv[2:]
        working_dir = Repository.get_working_dir()
        index = Index()

        if files_to_add == ["."]:
            files = Repository.find_files()
        else:
            files = []
            for pattern in files_to_add:
                abs_path = os.path.abspath(pattern)
                if os.path.isfile(abs_path):
                    files.append(abs_path)
                else:
                    print(f"Warning: '{pattern}' doesn't match any files")

        changed_files = 0
        for filepath in files:
            try:
                relative_path = Repository.get_relative_path(filepath, working_dir)
                content = FileHandler.read(filepath)

                if content is None:
                    continue

                current_hash = HashCalculate.calculate_sha1(content)
                existing_hash = index.get_entry(relative_path)

                if existing_hash == current_hash and ObjectStore.blob_exists(
                    current_hash
                ):
                    continue

                blob_hash = ObjectStore.store_blob(filepath)
                index.add_entry(relative_path, blob_hash)
                changed_files += 1
                print(f"Added {relative_path}")

            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")
                continue
        if changed_files > 0:
            index.save()
            print(f"Staged {changed_files} file(s)")
        else:
            print("Nothing to stage")

    def show_status(self):
        if not Repository.is_initialized():
            print("Not a questgit repository")
            return

        index = Index()
        working_dir = Repository.get_working_dir()
        tracked_files = set(index.entries.keys())
        all_files = set(
            Repository.get_relative_path(f, working_dir)
            for f in Repository.find_files()
        )

        print("Tracked files:")
        for file in sorted(tracked_files):
            status = "modified" if file in all_files else "deleted"
            print(f"\033[92m  {status}: {file}\033[0m")

        print("\nUntracked files:")
        for file in sorted(all_files - tracked_files):
            print(f"\033[91m  untracked: {file}\033[0m")

    def show_usage(self):
        print("Usage: questgit <command>")
        print("Available commands:")
        for cmd in self.commands.keys():
            print(f"  - {cmd}")

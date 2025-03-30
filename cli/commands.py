import sys
import os

from questgit.repository import Repository
from questgit.index import Index
from utils.file_utils import FileHandler
from questgit.objects import ObjectStore
from utils.hash_utils import HashCalculate
from utils.logger_utils import LoggerUtil
from questgit.config import Config

logger = LoggerUtil.setup_logger(__name__)


class CLIHandler:
    def __init__(self):
        self.commands = {
            "init": self.init_repo,
            "add": self.add_files,
            "status": self.show_status,
            "restore": self.restore_staged,
            "unstage": self.unstage,
            "config": self.config,
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

    # For Init command
    def init_repo(self):
        Repository.init()

    # For add command
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

    # For status command
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

    # For Restore command from staging area
    def restore_staged(self):
        if not Repository.is_initialized():
            print("Not a questgit repository")
            return

        index = Index()
        working_dir = Repository.get_working_dir()

        if not index.entries:
            print("No files in staging area")
            return

        files_to_restore = sys.argv[3:] if len(sys.argv) > 3 else None

        restored_files = 0
        for filepath, blob_hash in index.entries.items():
            if files_to_restore and filepath not in files_to_restore:
                continue

            try:
                content = ObjectStore.read_blob(blob_hash)
                if content is None:
                    print(f"Warning: Could not read blob for {filepath}")
                    continue

                abs_path = os.path.join(working_dir, filepath)
                FileHandler.write(abs_path, content)
                print(f"Restored {filepath}")
                restored_files += 1

            except Exception as e:
                logger.error(f"Error restoring {filepath}: {e}")

        if restored_files > 0:
            print(f"Restored {restored_files} file(s) from staging area")
        else:
            print("No files restored")

    # For unstage command from staging area
    def unstage(self):
        if not Repository.is_initialized():
            print("Not a questgit repository")
            return

        if len(sys.argv) < 3:
            print("Usage: questgit unstage <file1> [<file2> ...]")
            return

        index = Index()
        files_to_unstage = sys.argv[2:]
        working_dir = Repository.get_working_dir()

        removed_files = 0
        for filepath in files_to_unstage:
            if os.path.isabs(filepath):
                rel_path = Repository.get_relative_path(filepath, working_dir)
            else:
                rel_path = filepath

            if rel_path in index.entries:
                index.remove_entry(rel_path)
                print(f"Removed {rel_path} from staging area")
                removed_files += 1
            else:
                print(f"File not in staging area: {rel_path}")

        if removed_files > 0:
            index.save()
            print(f"Removed {removed_files} file(s) from staging area")
        else:
            print("No files removed from staging area")

    # For config command
    def validate_config(self):
        if not Config.validate_required():
            print("Error: Missing user configuration. Run:")
            print('  questgit config user.name "Your Name"')
            print('  questgit config user.email "your@email.com"')
            return False
        return True

    def config(self):

        if len(sys.argv) < 3:
            print("Usage: questgit config <key> <value>")
            print("       questgit config --check")
            return

        if sys.argv[2] == "--check":
            self.validate_config()
            return

        if len(sys.argv) != 4:
            print("Usage: questgit config <key> <value>")
            return

        Config.set(sys.argv[2], sys.argv[3])
        print(f"Set {sys.argv[2]}={sys.argv[3]}")

    def show_usage(self):
        print("Usage: questgit <command>")
        print("Available commands:")
        # for cmd in self.commands.keys():
        #     print(f"  - {cmd}")
        print("  init       - Initialize a new repository")
        print("  config     - Configure user settings")
        print("  add        - Add files to staging area")
        print("  status     - Show staged/unstaged changes")
        print("  restore    - Restore files from staging to working directory")
        print("  unstage    - Remove files from staging area")
        print("  commit     - Record changes to the repository")

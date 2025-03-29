import sys
from questgit.repository import Repository


class CLIHandler:
    def __init__(self):
        self.commands = {"init": self.init_repo}

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

    def show_usage(self):
        print("Usage: questgit <command>")
        print("Available commands:")
        for cmd in self.commands.keys():
            print(f"  - {cmd}")

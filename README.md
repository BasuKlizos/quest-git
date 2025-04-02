# README

## QuestGit

QuestGit is a command-line tool designed to manage repositories efficiently. Below is the list of available commands and their functionalities.

### Available Commands:

- **init**       - Initialize a new repository
- **config**     - Configure user settings
- **add**        - Add files to staging area
- **status**     - Show staged/unstaged changes
- **restore**    - Restore files from staging to working directory
- **unstage**    - Remove files from staging area
- **commit**     - Record changes to the repository
- **log**        - Display commit history

### Usage
To use these commands, run them in your terminal or command prompt within your repository directory. Example usage:

```sh
$ questgit init
$ questgit add filename
$ questgit commit -m "Commit message"
$ questgit log
```
### Other command
```sh
$ questgit config user.name <your_name>
$ questgit config user.email <your_email>
$ questgit restore filename
$ questgit unstage
$ questgit cat-file -p <hash>
```



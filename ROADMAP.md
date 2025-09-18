# Ruxpy Roadmap & Future Enhancements

This document outlines planned features, enhancements, and edge cases for the ruxpy version control system. It serves as a guide for future development and contributions.

## Upcoming Features

### 1. Enhanced `ruxpy scan` (Repository Status)
- Detect and list all files in the working directory that have been:
  - Modified since the last commit (starlog)
  - Newly created (untracked)
  - Deleted (missing from working directory but present in last commit)
- Compare the current state of files against the last committed (starlog) state using blob hashes.
- Show which files are staged (present in `.dock/stage`) and which are unstaged.
- Advise users if files can be staged with `beam` or committed with `starlog`.
- Display a clear summary of repository status, including:
  - Staged changes ready for commit
  - Unstaged changes
  - Untracked files
  - Clean state (no changes)

### 2. Edge Case Handling
- Binary files: Properly detect and display status for non-text files.
- Symlinks: Decide whether to track links or targets.
- Ignored files: Support a `.dockignore` file to exclude files from status.
- Renamed files: Detect and handle file renames.
- Permission changes: Track changes in file permissions.
- Large repositories: Optimize status checks for performance.
- Nested repositories: Avoid confusion with repos inside repos.
- Case sensitivity: Handle differences in filesystem case sensitivity.
- Non-UTF8 filenames: Support unusual filename encodings.

## Future Enhancements
- Branch management and switching
- Diff and patch generation
- Merge and conflict resolution
- Commit signing and verification
- Integration with remote repositories
- Advanced logging and history visualization

---

Contributions and suggestions are welcome! Please open issues or PRs to discuss new ideas or improvements.

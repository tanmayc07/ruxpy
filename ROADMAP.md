# Ruxpy Roadmap & Future Enhancements

This document outlines planned features, enhancements, and edge cases for the ruxpy version control system. It serves as a guide for future development and contributions.

## Upcoming Features
### Limitations & Future Improvements for `ruxpy starlog`
- Only staged files are included in the new commit; partial commits are not supported.
- Modified tracked files not staged are not updated in the new commit (previous hash remains).
- Deleted files are not detected or removed from the commit’s file list.
- Renames are treated as deletion and addition, not as a rename.
- Untracked files are not added unless explicitly staged; no warning or prompt for untracked files.
- No merge/conflict logic; advanced workflows are not supported.
- No validation of parent commit state for consistency (e.g., deleted/renamed files).
- Commit message validation is not enforced (empty messages allowed).

**Planned improvements:**
- Add logic for deleted files and commit message validation.
- Improve parent commit state management.
- Support for renames and merges in future versions.

### 1. Enhanced `ruxpy scan` (Repository Status)
- Detect and list all files in the working directory that have been:
  - Modified since the last commit (starlog)
  - Newly created (untracked)
  - Deleted (missing from working directory but present in last commit)
- Compare the current state of files against the last committed (starlog) state using blob hashes.
- Show which files are staged (present in `.dock/stage`) and which are unstaged.
- Advise users if files can be staged with `beam` or committed with `starlog`.
 Display a clear summary of repository status, including:
   - Staged changes ready for commit
   - Unstaged changes
   - Untracked files
   - Clean state (no changes)

 #### Planned Rust Refactor for Scan/Status
 - Move performance-critical and security-sensitive logic to Rust:
   - Blob hashing and file comparison (for modified/untracked detection)
   - Starlog (commit) reading and validation
   - Staging area management (read/write and compare)
   - Filesystem scanning (recursive listing, ignore rules, edge cases)
   - .dock integrity checks

 Python will orchestrate CLI and user interaction, calling Rust via PyO3 for heavy-lifting tasks.
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

### 3. `ruxpy course` Branch Management
- `ruxpy course -l`: List all branches ("courses") in the repository.
- `ruxpy course -sw <branch>`: Switch to a particular branch.
- `ruxpy course -c <branch>`: Create a new branch.


### 4. `ruxpy starlog`
- `ruxpy starlog -l`: List all starlogs (commits) in the repository.
- Interactive commit message: If `ruxpy starlog -c` is run without `-m`, open the default editor for the user to enter a commit message (similar to git).
- Support for `-m` flag: Allow `ruxpy starlog -c -m "message"` or `ruxpy starlog -cm "message"` to commit with a message directly from the terminal.

## Future Enhancements

- Branch management and switching
- Diff and patch generation
- Merge and conflict resolution
- Commit signing and verification
- Integration with remote repositories
- Advanced logging and history visualization

- Config command improvements:
  - Validation for config fields (e.g. email format, non-empty username/name)
  - User feedback when no options are provided (show current config or helpful message)


## Deployment & Release Plan

- Plan to package and release ruxpy as a Nix package for easy installation and usage across platforms.
- Provide reproducible development and deployment environments using Nix.

## Data Integrity & Atomic Writes

To ensure robust data integrity, implement atomic write operations for critical storage paths:

- Object store (blob storage):
  - Use atomic file writes to prevent corruption or partial writes during blob save operations.
- Starlog store (commit storage):
  - Apply atomic writes when saving starlogs to guarantee commit consistency.

Note: While atomic writes are less critical for config updates, they are essential for object and commit storage to avoid data loss or corruption in case of crashes or interruptions.

---

Contributions and suggestions are welcome! Please open issues or PRs to discuss new ideas or improvements.

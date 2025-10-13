# Ruxpy Roadmap & Future Enhancements

This document outlines planned features, enhancements, and edge cases for the ruxpy version control system. It serves as a guide for future development and contributions.

## Upcoming Features

### 1. Tree Data Structure Implementation for Project States
- Tree data structure implementation will represent the complete file and directory state of the project at each starlog entry.
- Each starlog entry (commit) will reference a tree object, which records the hierarchy and content hashes of all files and folders.
- This will enable efficient diffing, course switching and merging by allowing ruxpy to reconstruct and compare project states across history.

### 2. Switching Courses
Course switching will be provided using seperate command for better UX. The command will be:\
`ruxpy warp <course-name>`

### 3. Switching/Reverting on starlogs
An essential feature for reverting on starlog entries or going back on some particular starlog discarding the starlogs in between. Will be provided using the command:\
`ruxpy jump [OPTIONS] [STARLOG_HASH]`

Possible usage:

- `ruxpy jump <starlog-hash>` - Move the starlog pointer to a specific starlog-hash. (like `git checkout <commit>`)
- `ruxpy jump --back <number>` - Go back `<number>` number of starlogs. Like `git reset --hard HEAD~x`
- `ruxpy jump --delete-latest` - Delete the latest starlog.

### 4. `ruxpy starlog`
- Interactive commit message: If `ruxpy starlog -c` is run without `-m`, open the default editor for the user to enter a commit message (similar to git).

### 5. Config Management
- Validations for config keys
- Functionality to view the currently set config

### 6. Diffing
This is a required feature for implementing advanced workflows like checking changes, merge conflicts etc.
Yet to be designed.

## Data Integrity & Atomic Writes

To ensure robust data integrity, implement atomic write operations for critical storage paths:

- Object store (blob storage):
  - Use atomic file writes to prevent corruption or partial writes during blob save operations.
- Starlog store (commit storage):
  - Apply atomic writes when saving starlogs to guarantee commit consistency.

Note: While atomic writes are less critical for config updates, they are essential for object and commit storage to avoid data loss or corruption in case of crashes or interruptions.

---

Contributions and suggestions are welcome! Please open issues or PRs to discuss new ideas or improvements.

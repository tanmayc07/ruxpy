# Ruxpy Roadmap & Future Enhancements

This document outlines planned features, enhancements, and edge cases for the ruxpy version control system. It serves as a guide for future development and contributions.

## Upcoming Features

### 1. Branch Management
As per ruxpy nomenclature, a branch or seperate timeline will be named as a `course`. This feature will be provided using the command:\
`ruxpy course [OPTIONS] [ARG]`

Possible usage:

- `ruxpy course` - Listing all the courses with highlight for current active course
- `ruxpy course [-s | --set] <course-name>` - Create a new course
- `ruxpy course [-d | --delete] <course-name>` - delete a course 

> Note - As a design decision, the `core` course will be indestructible or default course. Also, since `core` can't be deleted, you need to be checked out on `core` to delete the last remaining course(other than `core` ofcourse).

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

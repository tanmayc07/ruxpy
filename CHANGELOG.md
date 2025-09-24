# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 

---

## [1.0.0] - 2025-09-24
### Added
- Initial public release of **ruxpy**, a hybrid Rust/Python version control system.
- `start` command: Initialize a new ruxpy repository.
- `config` command: Set username, email, and name for commits.
- `scan` command: Show repository status, including staged, modified, deleted, and untracked files.
- `beam` command: Stage files for the next starlog (commit), with support for `.dockignore` and robust file checks.
- `starlog` command: Create commits (starlogs), skip missing files, prevent empty commits, and manage parent/metadata.
- `.dockignore` support: Ignore files and directories using familiar patterns.
- Cross-platform wheel builds and GitHub Actions workflow for automated releases.
- User-friendly CLI output and error handling.

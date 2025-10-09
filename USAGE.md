# `ruxpy` Command Usage

## Table of Contents
- [Getting Started](#getting-started)
- [Commands](#commands)
  - [start](#start)
  - [beam](#beam)
  - [starlog](#starlog)
  - [scan](#scan)
  - [config](#config)
  - [course](#course)
- [Examples](#examples)

---

## Getting Started

### Install ruxpy from GitHub Releases

1. Go to the [ruxpy GitHub Releases page](https://github.com/<your-username>/ruxpy/releases).
2. Download the binary or wheel file for your platform (e.g., `.whl` for Python, or `.tar.gz`/`.zip` for CLI).
3. For Python users:
   ```sh
   pip install /path/to/ruxpy-<version>-<platform>.whl
   ```
    Or with uv:
    ```sh
    uv pip install /path/to/ruxpy-<version>-<platform>.whl
    ```

4. For CLI users:
- Add the binary to your PATH.
- Run `ruxpy --help` to verify installation.

### Note
- You must have Python and pip (or uv) installed for the wheel.
- No installation from PyPI is available; always use the latest release from GitHub.

### Commands

#### `start`
**Usage:**
`ruxpy start [<path>]`

**DESCRIPTION**

Initializes a new ruxpy project at the given path.

If executed without <path>, it initializes the project in current working directory. If <path> is passed, initializes at that location.

Does not create any initial commit. 

#### `beam`
**Usage:** `ruxpy beam <file>...`

**DESCRIPTION**

Stages files for the next starlog (commit).

Currently, there is no facility to use '.' or do bulk beam using any options. It is included in the feature roadmap.

#### `starlog`
**Usage:** `ruxpy starlog [-l] [-cm <message>]`

**DESCRIPTION**

Records a new starlog (commit) entry or lists previous starlog entries.

**OPTIONS**

**-l** \
**--list**\
Lists the previous starlog entries

**-c**
**--create**\
**-m**
**--message**\
Create a new starlog with the message. Currently, if message is not passed, returns an error specifying message required.

#### `scan`

**Usage:** `ruxpy scan`

**DESCRIPTION**

Shows the repository status, including beamed, modified, and untracked files.

#### `config`

**Usage:** `ruxpy config [-sn <name>] [-se <email>] [-su <username>]`

**DESCRIPTION**

Sets user configuration for starlogs.

#### `course`

**Usage:** `ruxpy course`

**DESCRIPTION**

Lists all branches (courses) and shows the current one. The default branch created when `ruxpy start` is executed is named `core`.

### Examples

```sh
# Initialize a project
ruxpy start

# Stage files
ruxpy beam file1.txt file2.txt

# Commit changes
ruxpy starlog -cm "Initial commit"

# View status
ruxpy scan

# List branches
ruxpy course

```




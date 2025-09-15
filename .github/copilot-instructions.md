# Copilot Instructions for AI Coding Agents

## Project Overview
- **ruxpy** is a Python/Rust hybrid project, exposing Rust functionality to Python via a compiled extension (`ruxpy.cpython-312-darwin.so`).
- The Rust source is in `src/` (main: `lib.rs`). Python interface and CLI are in `ruxpy/`.
- The build system uses Cargo (Rust) and Python packaging (PEP 517/pyproject.toml). Wheels are output to `target/wheels/`.

## Architecture & Data Flow
- Rust code in `src/lib.rs` provides core logic, compiled as a shared library.
- Python code in `ruxpy/` loads the Rust extension and exposes CLI (`cli.py`) and API (`__init__.py`).
- Communication between Python and Rust is via PyO3 bindings.

## Developer Workflows
- **Build Rust extension:**
  - Run `cargo build --release` to build the Rust library.
  - Use `maturin build` or `maturin develop` to build and install the Python extension locally.
- **Python packaging:**
  - `pyproject.toml` configures build dependencies and entry points.
  - Wheels are generated in `target/wheels/`.
- **CLI usage:**
  - Entry point is `ruxpy/cli.py`. Exposes main commands for users.
- **Debugging:**
  - For Rust: Use `cargo test` and standard Rust debugging tools.
  - For Python: Use standard Python debuggers; extension must be rebuilt after Rust changes.

## Project-Specific Conventions
- All Python code that calls Rust must import from the compiled `.so` file in `ruxpy/`.
- Rust functions exposed to Python use `#[pyfunction]` and are registered in `lib.rs`.
- CLI logic is centralized in `ruxpy/cli.py`.
- Build artifacts are not checked in; always rebuild after code changes.

## Integration Points
- **PyO3** is the bridge between Rust and Python. See `src/lib.rs` for exposed functions.
- **Maturin** is used for building and packaging the extension.
- **Cargo** manages Rust dependencies and builds.

## Key Files & Directories
- `src/lib.rs`: Rust logic and Python bindings
- `ruxpy/cli.py`: Python CLI entry point
- `ruxpy/__init__.py`: Python API surface
- `pyproject.toml`: Python build configuration
- `Cargo.toml`: Rust build configuration
- `ruxpy/ruxpy.cpython-312-darwin.so`: Compiled extension

## Example Patterns
- To expose a Rust function to Python:
  ```rust
  #[pyfunction]
  fn my_func(...) -> PyResult<...> { ... }
  ```
  Register in `lib.rs` with `m.add_function(wrap_pyfunction!(my_func, m)?)`.
- To call from Python:
  ```python
  from ruxpy import my_func
  result = my_func(...)
  ```

---

If any section is unclear or missing details, please specify which workflows, conventions, or integration points need further documentation.
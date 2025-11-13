# ruxpy

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/tanmayc07/ruxpy/.github%2Fworkflows%2FCI.yml
)
![GitHub last commit](https://img.shields.io/github/last-commit/tanmayc07/ruxpy)
![GitHub issues](https://img.shields.io/github/issues/tanmayc07/ruxpy)
![GitHub](https://img.shields.io/github/license/tanmayc07/ruxpy)

> **ruxpy** is a Star Trek-themed, hybrid Rust+Python version control system.  
> 🚧 **This project is under active development. Opinions, feedback, and contributions are welcome!** 🚧

## Features

- Fast object store powered by Rust
- Modern Python CLI for repository management
- Staging, commit and branching logic
- Star Trek-inspired naming and UX

## Installation and Usage
Pre-built wheel files for Windows, macOS, and Linux are available on the [GitHub Releases](https://github.com/tanmayc07/ruxpy/releases) page.
For detailed installation steps and a list of available commands, see the [USAGE.md](./USAGE.md) documentation.

## Development

```bash
# Clone the repo
git clone https://github.com/tanmayc07/ruxpy.git
cd ruxpy

# Install Nix (if not already installed)
curl -L https://nixos.org/nix/install | sh

# Enable Nix flakes (add to ~/.config/nix/nix.conf):
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

# Create and activate a venv
uv venv
source .venv/bin/activate

# Install python dependencies (using uv)
uv pip install -r requirements.txt

# Enter the nix shell (requires Nix and flakes)
nix develop

# Install the pre-commit hook if its your first time after cloning the repo
pre-commit install

# Build the Rust extension
maturin develop
```

## Contributing
- The project is in its early stages—ideas and help are appreciated!
- Please open issues or pull requests for suggestions, bug reports, or improvements.
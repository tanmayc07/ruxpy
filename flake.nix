{
  description = "Ruxpy development environment";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
  };
  outputs = { self, nixpkgs, flake-utils, rust-overlay }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; overlays = [(import rust-overlay)]; };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pkgs.python312Full
            pkgs.rust-bin.stable.latest.default
            pkgs.cargo
            pkgs.maturin
            pkgs.git
            pkgs.python312Packages.pip
            pkgs.python312Packages.uv
            pkgs.python312Packages.click
            pkgs.python312Packages.black
            pkgs.python312Packages.flake8
            pkgs.python312Packages.tomlkit
            pkgs.python312Packages.pytest
            pkgs.python312Packages.setuptools
            pkgs.python312Packages.wheel
          ];
          shellHook = ''
            [ -f ~/.bashrc ] && source ~/.bashrc
            export PS1="\[\033[0;32m\](ruxpy-nix) \[\033[0m\]$PS1"

            if [ -n "$VIRTUAL_ENV" ]; then
              export PS1="\[\033[0;32m\][venv:$(basename $VIRTUAL_ENV)]\[\033[0m\] $PS1"
            else
              export PS1="(no-venv) $PS1"
            fi
            echo "Welcome to the Ruxpy dev environment!"
            echo "Python: $(python3 --version)"
            echo "Rust: $(rustc --version)"
            echo "Maturin: $(maturin --version)"
            echo "run maturin develop to start using ruxpy"
          '';
        };
      }
    );
}

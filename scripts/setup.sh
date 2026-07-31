#!/usr/bin/env sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VENV_DIR=${VENV_DIR:-"$REPO_ROOT/.venv"}
EXTRAS=${1:-dev}

run_as_root() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    else
        printf '%s\n' "Administrator access is required to install Foma: $*" >&2
        exit 1
    fi
}

install_foma() {
    if command -v brew >/dev/null 2>&1; then
        brew install foma
    elif command -v apt-get >/dev/null 2>&1; then
        run_as_root apt-get update
        run_as_root apt-get install -y foma-bin
    elif command -v dnf >/dev/null 2>&1; then
        run_as_root dnf install -y foma
    elif command -v pacman >/dev/null 2>&1; then
        run_as_root pacman -S --needed foma
    else
        printf '%s\n' \
            "flookup is required, but no supported package manager was found." \
            "Install Foma from https://fomafst.github.io/ and rerun this script." >&2
        exit 1
    fi
}

if ! command -v flookup >/dev/null 2>&1; then
    printf '%s\n' "flookup was not found; installing Foma..."
    install_foma
fi

if ! command -v flookup >/dev/null 2>&1; then
    printf '%s\n' "Foma installation completed, but flookup is still not on PATH." >&2
    exit 1
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -e "$REPO_ROOT[$EXTRAS]"

printf '%s\n' \
    "Setup complete." \
    "Activate the environment with: . $VENV_DIR/bin/activate" \
    "Run the tests with: $VENV_DIR/bin/pytest"

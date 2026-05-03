#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${PYTHONETTE_REPO:-https://github.com/roxxorarc/pythonette-42.git}"
REPO_BRANCH="${PYTHONETTE_BRANCH:-main}"
PREFIX_DIR="${PYTHONETTE_PREFIX:-${HOME}/.local/share/pythonette}"
BIN_DIR="${PYTHONETTE_BIN:-${HOME}/.local/bin}"
VENV_DIR="${PREFIX_DIR}/venv"
SRC_DIR="${PREFIX_DIR}/src"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    REPO_DIR="$SCRIPT_DIR"
else
    if ! command -v git >/dev/null 2>&1; then
        echo "error: git not found in PATH" >&2
        exit 1
    fi
    if [ -d "$SRC_DIR/.git" ]; then
        git -C "$SRC_DIR" fetch --quiet origin "$REPO_BRANCH"
        git -C "$SRC_DIR" reset --quiet --hard "origin/$REPO_BRANCH"
    else
        mkdir -p "$PREFIX_DIR"
        git clone --quiet --branch "$REPO_BRANCH" --depth 1 "$REPO_URL" "$SRC_DIR"
    fi
    REPO_DIR="$SRC_DIR"
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 not found in PATH" >&2
    exit 1
fi

PYVER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
case "$PYVER" in
    3.10|3.11|3.12|3.13) ;;
    *) echo "error: python >= 3.10 required (found $PYVER)" >&2; exit 1 ;;
esac

mkdir -p "$PREFIX_DIR" "$BIN_DIR"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" 2>/dev/null || python3 -m venv --without-pip "$VENV_DIR"
fi

if [ ! -x "$VENV_DIR/bin/pip" ]; then
    GET_PIP="$(mktemp)"
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o "$GET_PIP"
    "$VENV_DIR/bin/python" "$GET_PIP" --quiet
    rm -f "$GET_PIP"
fi

"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet --upgrade -e "$REPO_DIR"

WRAPPER="$BIN_DIR/pythonette"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/pythonette" "\$@"
EOF
chmod +x "$WRAPPER"

echo "installed: $WRAPPER -> $VENV_DIR/bin/pythonette"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        RC="${HOME}/.zshrc"
        LINE="export PATH=\"$BIN_DIR:\$PATH\""
        if [ -f "$RC" ] && ! grep -qF "$LINE" "$RC"; then
            printf '\n# added by pythonette installer\n%s\n' "$LINE" >> "$RC"
            echo "added $BIN_DIR to PATH in $RC — run: source $RC"
        else
            echo "warning: $BIN_DIR is not in PATH — add to your shell rc:"
            echo "    $LINE"
        fi
        ;;
esac

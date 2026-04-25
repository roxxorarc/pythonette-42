#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX_DIR="${PYTHONETTE_PREFIX:-${HOME}/.local/share/pythonette}"
BIN_DIR="${PYTHONETTE_BIN:-${HOME}/.local/bin}"
VENV_DIR="${PREFIX_DIR}/venv"

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
    python3 -m venv "$VENV_DIR"
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
    *) echo "warning: $BIN_DIR is not in PATH — add to ~/.zshrc or ~/.bashrc:"
       echo "    export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac

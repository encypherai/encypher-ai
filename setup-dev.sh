#!/usr/bin/env bash

set -u

SKIP_PYTHON=false
SKIP_NODE=false
SHOW_HELP=false

print_help() {
  cat <<'EOF'
Usage: ./setup-dev.sh [options]

Options:
  --skip-python   Skip Python/UV dependency installation
  --skip-node     Skip Node/Next.js dependency installation
  --help          Show this help message

This script installs all dependencies needed for local development on Linux/macOS:
- Python workspace deps via UV (recommended: uv sync --all-packages)
- Frontend deps for Next.js apps via npm install
EOF
}

log_info() {
  printf "%s\n" "$1"
}

log_ok() {
  printf "  [OK] %s\n" "$1"
}

log_err() {
  printf "  [ERR] %s\n" "$1" >&2
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-python)
      SKIP_PYTHON=true
      ;;
    --skip-node)
      SKIP_NODE=true
      ;;
    --help|-h)
      SHOW_HELP=true
      ;;
    *)
      log_err "Unknown argument: $1"
      print_help
      exit 2
      ;;
  esac
  shift

done

if [ "$SHOW_HELP" = true ]; then
  print_help
  exit 0
fi

if [ "$SKIP_PYTHON" = false ]; then
  if ! have_cmd uv; then
    log_err "uv is not installed. Install it first: https://github.com/astral-sh/uv"
    exit 1
  fi

  log_info "Installing Python workspace dependencies (uv sync --all-packages)..."
  uv sync --all-packages
  log_ok "Python dependencies installed"
else
  log_info "Skipping Python dependency installation (--skip-python)"
fi

if [ "$SKIP_NODE" = false ]; then
  if ! have_cmd node; then
    log_err "Node.js is not installed (requires Node 24+ LTS)"
    exit 1
  fi
  if ! have_cmd npm; then
    log_err "npm is not installed"
    exit 1
  fi

  log_info "Installing frontend dependencies (npm install)..."

  if [ -d "apps/marketing-site" ]; then
    (cd "apps/marketing-site" && npm install)
    log_ok "apps/marketing-site dependencies installed"
  else
    log_err "apps/marketing-site not found"
    exit 1
  fi

  if [ -d "apps/dashboard" ]; then
    (cd "apps/dashboard" && npm install)
    log_ok "apps/dashboard dependencies installed"
  else
    log_err "apps/dashboard not found"
    exit 1
  fi
else
  log_info "Skipping Node dependency installation (--skip-node)"
fi

log_ok "Setup complete"

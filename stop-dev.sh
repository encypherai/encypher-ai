#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

step() {
  echo
  echo "[$1] $2"
}

ok() {
  echo "  [OK] $1"
}

warn() {
  echo "  [WARN] $1" >&2
}

compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  else
    echo "docker-compose"
  fi
}

kill_port() {
  local port="$1"

  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti TCP:"${port}" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$pids" ]]; then
      echo "$pids" | xargs -r kill -9 || true
      ok "Stopped process(es) listening on port ${port}"
    fi
    return 0
  fi

  if command -v fuser >/dev/null 2>&1; then
    if fuser -k "${port}/tcp" >/dev/null 2>&1; then
      ok "Stopped process(es) listening on port ${port}"
    fi
    return 0
  fi

  warn "Neither lsof nor fuser available; cannot stop process on port ${port}"
}

step "1/2" "Stopping Docker containers..."
if command -v docker >/dev/null 2>&1; then
  COMPOSE="$(compose_cmd)"
  ${COMPOSE} -f docker-compose.full-stack.yml down || true
  ok "Docker containers stopped"
else
  warn "Docker not installed; skipping Docker shutdown"
fi

step "2/2" "Stopping frontend processes..."
kill_port 3000
kill_port 3001
kill_port 3002

ok "All services stopped"

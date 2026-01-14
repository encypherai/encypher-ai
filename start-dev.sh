#!/usr/bin/env bash
set -euo pipefail

SKIP_DOCKER=0
SKIP_FRONTEND=0
CLEAN_START=0

usage() {
  cat <<'EOF'
Usage: ./start-dev.sh [options]

Options:
  --skip-docker       Skip starting Docker services (use if already running)
  --skip-frontend     Skip starting frontend applications
  --clean-start       Clean rebuild (docker volumes, next caches, node cache)
  -h, --help          Show this help message

Examples:
  ./start-dev.sh
  ./start-dev.sh --clean-start
  ./start-dev.sh --skip-docker
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-docker)
      SKIP_DOCKER=1
      ;;
    --skip-frontend)
      SKIP_FRONTEND=1
      ;;
    --clean-start)
      CLEAN_START=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

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

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "  [ERR] Missing required command: $1" >&2
    exit 1
  fi
}

install_node_deps_if_needed() {
  local app_dir="$1"

  if [[ -d "${app_dir}/node_modules" ]]; then
    return 0
  fi

  if [[ -f "${app_dir}/package-lock.json" ]]; then
    npm ci
  else
    npm install
  fi
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local max_retries="${3:-30}"

  require_cmd curl

  local i
  for ((i=1; i<=max_retries; i++)); do
    if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
      ok "${name} is ready (${url})"
      return 0
    fi
    echo "    Waiting for ${name}... (${i}/${max_retries})"
    sleep 2
  done

  warn "${name} did not become ready in time (${url})"
  return 1
}

compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  else
    echo "docker-compose"
  fi
}

step "1/6" "Checking prerequisites..."
require_cmd node
require_cmd npm
ok "Node: $(node --version)"
ok "NPM: $(npm --version)"

COMPOSE=""
if [[ "$SKIP_DOCKER" -eq 0 ]]; then
  require_cmd docker
  if ! docker info >/dev/null 2>&1; then
    echo "  [ERR] Docker is not running" >&2
    exit 1
  fi
  ok "Docker is running"

  COMPOSE="$(compose_cmd)"
  if ! ${COMPOSE} version >/dev/null 2>&1; then
    echo "  [ERR] Docker Compose is not available" >&2
    exit 1
  fi
  ok "Docker Compose: $(${COMPOSE} version | head -n 1)"
fi

step "2/6" "Cleaning caches (optional)..."
if [[ "$CLEAN_START" -eq 1 ]]; then
  if [[ -d "apps/marketing-site/.next" ]]; then
    rm -rf "apps/marketing-site/.next"
  fi
  if [[ -d "apps/dashboard/.next" ]]; then
    rm -rf "apps/dashboard/.next"
  fi
  if [[ -d "apps/marketing-site/node_modules/.cache" ]]; then
    rm -rf "apps/marketing-site/node_modules/.cache"
  fi
  if [[ -d "apps/dashboard/node_modules/.cache" ]]; then
    rm -rf "apps/dashboard/node_modules/.cache"
  fi

  if [[ "$SKIP_DOCKER" -eq 0 ]]; then
    ${COMPOSE} -f docker-compose.full-stack.yml down -v >/dev/null 2>&1 || true
  fi

  ok "Clean start applied"
else
  ok "Skipping cache clean (use --clean-start to clean)"
fi

step "3/6" "Starting Docker services (optional)..."
if [[ "$SKIP_DOCKER" -eq 0 ]]; then
  if [[ "$CLEAN_START" -eq 0 ]]; then
    ${COMPOSE} -f docker-compose.full-stack.yml down >/dev/null 2>&1 || true
  fi

  if [[ "$CLEAN_START" -eq 1 ]]; then
    ${COMPOSE} -f docker-compose.full-stack.yml up -d --build --force-recreate
  else
    ${COMPOSE} -f docker-compose.full-stack.yml up -d
  fi

  ok "Docker services starting"
else
  ok "Skipping Docker (--skip-docker)"
fi

step "4/6" "Waiting for key services (optional)..."
if [[ "$SKIP_DOCKER" -eq 0 ]]; then
  for i in $(seq 1 30); do
    if docker exec encypher-postgres pg_isready -U encypher -d encypher_auth >/dev/null 2>&1; then
      ok "PostgreSQL is ready (host port ${POSTGRES_HOST_PORT:-15432})"
      break
    fi
    echo "    Waiting for PostgreSQL... (${i}/30)"
    sleep 2
  done

  if docker exec encypher-redis-cache redis-cli ping 2>/dev/null | grep -q "PONG"; then
    ok "Redis cache is ready (6379)"
  else
    warn "Redis cache did not respond"
  fi

  wait_for_http "Auth Service" "http://localhost:8001/health" 30 || true
  wait_for_http "Key Service" "http://localhost:8003/health" 30 || true
  wait_for_http "Enterprise API" "http://localhost:9000/health" 30 || true
else
  ok "Skipping service waits (Docker skipped)"
fi

MARKETING_PID=""
DASHBOARD_PID=""
MARKETING_TAIL_PID=""
DASHBOARD_TAIL_PID=""

cleanup() {
  step "" "Shutting down..."

  if [[ -n "${MARKETING_TAIL_PID}" ]]; then
    kill "${MARKETING_TAIL_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${DASHBOARD_TAIL_PID}" ]]; then
    kill "${DASHBOARD_TAIL_PID}" >/dev/null 2>&1 || true
  fi

  if [[ -n "${MARKETING_PID}" ]]; then
    kill "${MARKETING_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${DASHBOARD_PID}" ]]; then
    kill "${DASHBOARD_PID}" >/dev/null 2>&1 || true
  fi

  ok "Frontend processes stopped"
}

trap cleanup EXIT INT TERM

step "5/6" "Starting frontends (optional)..."
if [[ "$SKIP_FRONTEND" -eq 0 ]]; then
  LOG_DIR="${REPO_ROOT}/.tmp/dev-logs"
  mkdir -p "$LOG_DIR"

  MARKETING_LOG="${LOG_DIR}/marketing-site.log"
  DASHBOARD_LOG="${LOG_DIR}/dashboard.log"

  : >"$MARKETING_LOG"
  : >"$DASHBOARD_LOG"

  (
    cd "${REPO_ROOT}/apps/marketing-site"
    install_node_deps_if_needed "${REPO_ROOT}/apps/marketing-site"
    npm run dev
  ) >"$MARKETING_LOG" 2>&1 &
  MARKETING_PID="$!"

  (
    cd "${REPO_ROOT}/apps/dashboard"
    install_node_deps_if_needed "${REPO_ROOT}/apps/dashboard"
    npm run dev
  ) >"$DASHBOARD_LOG" 2>&1 &
  DASHBOARD_PID="$!"

  ok "Marketing Site starting on http://localhost:3000"
  ok "Dashboard starting on http://localhost:3001"

  require_cmd tail
  require_cmd sed
  require_cmd stdbuf

  stdbuf -oL -eL tail -n +1 -F "$MARKETING_LOG" | sed -u 's/^/[marketing] /' &
  MARKETING_TAIL_PID="$!"

  stdbuf -oL -eL tail -n +1 -F "$DASHBOARD_LOG" | sed -u 's/^/[dashboard] /' &
  DASHBOARD_TAIL_PID="$!"
else
  ok "Skipping frontends (--skip-frontend)"
fi

step "6/6" "Summary"
echo "  API Gateway:    http://localhost:8000"
echo "  Traefik UI:     http://localhost:8080"
echo "  Enterprise API: http://localhost:9000"
echo "  Marketing:      http://localhost:3000"
echo "  Dashboard:      http://localhost:3001"
echo

echo "Press Ctrl+C to stop streaming logs." 

if [[ -n "${MARKETING_PID}" || -n "${DASHBOARD_PID}" ]]; then
  wait
fi

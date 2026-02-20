#!/usr/bin/env bash
set -euo pipefail

SKIP_DOCKER=0
SKIP_FRONTEND=0
CLEAN_START=0
SKIP_DOCKER_LOGS=0
REBUILD_SERVICES=0
SKIP_STRIPE_LISTEN=0
STRIPE_WEBHOOK_FORWARD_URL="${STRIPE_WEBHOOK_FORWARD_URL:-localhost:8007/api/v1/webhooks/stripe}"

usage() {
  cat <<'EOF'
Usage: ./start-dev.sh [options]

Options:
  --skip-docker       Skip starting Docker services (use if already running)
  --skip-frontend     Skip starting frontend applications
  --clean-start       Clean rebuild (docker volumes, next caches, node cache)
  --rebuild           Rebuild application services (non-database) + clear .next caches
  --skip-docker-logs  Skip streaming Docker logs
  --skip-stripe-listen  Skip starting Stripe CLI webhook listener
  -h, --help          Show this help message

Examples:
  ./start-dev.sh
  ./start-dev.sh --rebuild
  ./start-dev.sh --clean-start
  ./start-dev.sh --skip-docker
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rebuild)
      REBUILD_SERVICES=1
      ;;
    --skip-docker)
      SKIP_DOCKER=1
      ;;
    --skip-frontend)
      SKIP_FRONTEND=1
      ;;
    --clean-start)
      CLEAN_START=1
      ;;
    --skip-docker-logs)
      SKIP_DOCKER_LOGS=1
      ;;
    --skip-stripe-listen)
      SKIP_STRIPE_LISTEN=1
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

compose_build_with_fallback() {
  local compose_file="$1"
  local services="$2"

  if ${COMPOSE} -f "$compose_file" build $services; then
    return 0
  fi

  warn "BuildKit build failed; retrying with legacy builder (DOCKER_BUILDKIT=0)"
  DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 ${COMPOSE} -f "$compose_file" build $services
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
  if [[ "$SKIP_DOCKER" -eq 0 ]]; then
    # Removes all containers AND named volumes (node_modules, .next caches, DB data)
    ${COMPOSE} -f docker-compose.full-stack.yml down -v >/dev/null 2>&1 || true
  fi

  ok "Clean start applied (Docker volumes removed)"
else
  ok "Skipping cache clean (use --clean-start to clean)"
fi

step "3/6" "Starting Docker services (optional)..."
if [[ "$SKIP_DOCKER" -eq 0 ]]; then
  if [[ "$CLEAN_START" -eq 0 ]]; then
    ${COMPOSE} -f docker-compose.full-stack.yml down >/dev/null 2>&1 || true
  fi

  if [[ "$REBUILD_SERVICES" -eq 1 ]]; then
    step "  " "Clearing stale .next caches for frontends..."
    # TEAM_155: Remove named .next cache volumes so Webpack chunks are rebuilt
    # from scratch. Stale chunks cause "Cannot read properties of undefined
    # (reading 'call')" errors with next/dynamic after code changes.
    for vol in marketing_next_cache dashboard_next_cache; do
      full_vol=$(docker volume ls -q --filter "name=${vol}" 2>/dev/null | head -1)
      if [[ -n "$full_vol" ]]; then
        docker volume rm "$full_vol" >/dev/null 2>&1 && ok "Removed volume ${full_vol}" || warn "Could not remove ${full_vol} (may be in use)"
      fi
    done

    step "  " "Clearing frontend node_modules volumes for dependency refresh..."
    # --rebuild should refresh JS dependencies inside Docker volumes too.
    # Otherwise, newly added packages in package.json can be missing at runtime.
    for vol in marketing_node_modules marketing_ds_node_modules dashboard_node_modules dashboard_ds_node_modules; do
      full_vol=$(docker volume ls -q --filter "name=${vol}" 2>/dev/null | head -1)
      if [[ -n "$full_vol" ]]; then
        docker volume rm "$full_vol" >/dev/null 2>&1 && ok "Removed volume ${full_vol}" || warn "Could not remove ${full_vol} (may be in use)"
      fi
    done

    step "  " "Rebuilding application services..."
    SERVICES_TO_BUILD="auth-service user-service key-service encoding-service verification-service coalition-service analytics-service billing-service notification-service enterprise-api marketing-site dashboard"
    compose_build_with_fallback "docker-compose.full-stack.yml" "$SERVICES_TO_BUILD"
  fi

  # Build the list of services to exclude
  COMPOSE_UP_ARGS=""
  if [[ "$SKIP_FRONTEND" -eq 1 ]]; then
    COMPOSE_UP_ARGS="--scale marketing-site=0 --scale dashboard=0"
  fi

  if [[ "$CLEAN_START" -eq 1 ]]; then
    ${COMPOSE} -f docker-compose.full-stack.yml up -d --build --force-recreate $COMPOSE_UP_ARGS
  else
    ${COMPOSE} -f docker-compose.full-stack.yml up -d $COMPOSE_UP_ARGS
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

  if [[ "$SKIP_FRONTEND" -eq 0 ]]; then
    wait_for_http "Marketing Site" "http://localhost:3000" 60 || true
    wait_for_http "Dashboard" "http://localhost:3001" 60 || true
  fi
else
  ok "Skipping service waits (Docker skipped)"
fi

DOCKER_LOG_PID=""
STRIPE_LISTEN_PID=""

cleanup() {
  step "" "Shutting down..."

  if [[ -n "${DOCKER_LOG_PID}" ]]; then
    kill "${DOCKER_LOG_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${STRIPE_LISTEN_PID}" ]]; then
    kill "${STRIPE_LISTEN_PID}" >/dev/null 2>&1 || true
  fi

  ok "Background processes stopped"
}

trap cleanup EXIT INT TERM

step "5/6" "Frontends (via Docker)..."
if [[ "$SKIP_FRONTEND" -eq 0 ]]; then
  ok "Marketing Site & Dashboard managed by Docker Compose"
  ok "Marketing Site: http://localhost:3000"
  ok "Dashboard:      http://localhost:3001"
else
  ok "Skipping frontends (--skip-frontend)"
fi

if [[ "$SKIP_STRIPE_LISTEN" -eq 0 ]]; then
  step "" "Starting Stripe webhook listener"
  if command -v stripe >/dev/null 2>&1; then
    stripe listen --forward-to "${STRIPE_WEBHOOK_FORWARD_URL}" &
    STRIPE_LISTEN_PID="$!"
    ok "Stripe CLI listening → ${STRIPE_WEBHOOK_FORWARD_URL}"
  else
    warn "Stripe CLI not found; install it or run with --skip-stripe-listen"
  fi
else
  ok "Skipping Stripe webhook listener (--skip-stripe-listen)"
fi

if [[ "$SKIP_DOCKER" -eq 0 && "$SKIP_DOCKER_LOGS" -eq 0 ]]; then
  step "" "Streaming Docker logs"
  require_cmd awk
  require_cmd stdbuf
  LOG_COLOR_RESET="\033[0m"
  stdbuf -oL -eL ${COMPOSE} -f docker-compose.full-stack.yml logs -f --tail=50 \
    | awk -v reset="$LOG_COLOR_RESET" '
      BEGIN {
        color["traefik"]="\033[38;5;39m"
        color["postgres"]="\033[38;5;69m"
        color["redis-cache"]="\033[38;5;73m"
        color["redis-celery"]="\033[38;5;73m"
        color["auth-service"]="\033[38;5;112m"
        color["key-service"]="\033[38;5;178m"
        color["enterprise-api"]="\033[38;5;81m"
        color["analytics-service"]="\033[38;5;141m"
        color["verification-service"]="\033[38;5;141m"
        color["billing-service"]="\033[38;5;214m"
        color["notification-service"]="\033[38;5;173m"
        color["user-service"]="\033[38;5;110m"
        color["encoding-service"]="\033[38;5;76m"
        color["coalition-service"]="\033[38;5;212m"
        color["marketing-site"]="\033[38;5;51m"
        color["dashboard"]="\033[38;5;207m"
        color["grafana"]="\033[38;5;208m"
        color["prometheus"]="\033[38;5;244m"
        color["jaeger"]="\033[38;5;216m"
      }
      {
        split($0, parts, "|")
        service=parts[1]
        gsub(/[[:space:]]+$/, "", service)
        msg=substr($0, length(parts[1]) + 2)
        if (service in color) {
          printf "%s[%s]%s%s\n", color[service], service, reset, msg
        } else {
          print $0
        }
      }
    ' &
  DOCKER_LOG_PID="$!"
fi

step "6/6" "Summary"
echo "  API Gateway:    http://localhost:8000"
echo "  Traefik UI:     http://localhost:8080"
echo "  Enterprise API: http://localhost:9000"
echo "  Marketing:      http://localhost:3000"
echo "  Dashboard:      http://localhost:3001"
echo

echo "Press Ctrl+C to stop streaming logs." 

if [[ -n "${DOCKER_LOG_PID}" || -n "${STRIPE_LISTEN_PID}" ]]; then
  wait
fi

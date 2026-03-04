#!/usr/bin/env bash
set -euo pipefail

SERVICE="exa.extension_server_pb.ExtensionServerService"

usage() {
  cat <<'EOF'
Usage:
  windsurf_terminal_bridge.sh status
  windsurf_terminal_bridge.sh shell-support
  windsurf_terminal_bridge.sh search "query text"
  windsurf_terminal_bridge.sh read-terminal [terminal_id]
  windsurf_terminal_bridge.sh rpc <MethodName> [json_payload]

Notes:
  - Discovers CSRF token and extension server port from active Windsurf language server process.
  - Calls local Windsurf extension server RPC endpoint on 127.0.0.1.
EOF
}

extract_arg() {
  local flag="$1"
  local cmdline="$2"
  awk -v flag="$flag" '
    $0 == flag { getline; print; exit }
  ' <<<"$cmdline"
}

discover_runtime() {
  local pid
  pid="$(pgrep -f 'language_server_linux_x64.*--extension_server_port' | tail -n 1 || true)"
  if [[ -z "$pid" ]]; then
    echo "No active Windsurf language server process found" >&2
    exit 1
  fi

  local cmdline
  cmdline="$(tr '\0' '\n' < "/proc/${pid}/cmdline")"

  WS_PORT="$(extract_arg "--extension_server_port" "$cmdline")"
  WS_TOKEN="$(extract_arg "--csrf_token" "$cmdline")"

  if [[ -z "${WS_PORT:-}" || -z "${WS_TOKEN:-}" ]]; then
    echo "Failed to discover Windsurf extension server port or CSRF token" >&2
    exit 1
  fi

  export WS_PID="$pid"
  export WS_PORT
  export WS_TOKEN
}

rpc_call() {
  local method="$1"
  local payload="${2-}"
  if [[ -z "$payload" ]]; then
    payload='{}'
  fi

  discover_runtime

  local url="http://127.0.0.1:${WS_PORT}/${SERVICE}/${method}"
  curl -sS --fail-with-body \
    -H "x-codeium-csrf-token: ${WS_TOKEN}" \
    -H 'content-type: application/json' \
    -H 'connect-protocol-version: 1' \
    --data "$payload" \
    "$url"
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  printf '%s' "$value"
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    status)
      discover_runtime
      printf '{"pid":%s,"port":%s,"token_prefix":"%s"}\n' "$WS_PID" "$WS_PORT" "${WS_TOKEN:0:8}"
      ;;
    shell-support)
      rpc_call "CheckTerminalShellSupport" '{}'
      ;;
    search)
      if [[ $# -lt 2 ]]; then
        echo "Missing query" >&2
        usage
        exit 1
      fi
      local q
      q="$(json_escape "$2")"
      rpc_call "SearchQuery" "{\"query\":\"${q}\"}"
      ;;
    read-terminal)
      if [[ $# -ge 2 ]]; then
        local tid
        tid="$(json_escape "$2")"
        rpc_call "ReadTerminal" "{\"terminalId\":\"${tid}\"}"
      else
        rpc_call "ReadTerminal" '{}'
      fi
      ;;
    rpc)
      if [[ $# -lt 2 ]]; then
        echo "Missing method name" >&2
        usage
        exit 1
      fi
      local method payload
      method="$2"
      payload="${3-}"
      rpc_call "$method" "$payload"
      ;;
    ""|-h|--help)
      usage
      ;;
    *)
      echo "Unknown command: $cmd" >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"

#!/bin/bash
# Supervised CC Webhook Receiver runner.
# Auto-restarts on crash. Writes PID file so reapers can identify it.
#
# Usage:
#   ./run-receiver.sh          # foreground
#   ./run-receiver.sh daemon    # background (nohup + disowned)
#   ./run-receiver.sh stop      # stop running instance
#   ./run-receiver.sh status    # check if running

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.receiver"
PID_FILE="${SCRIPT_DIR}/.receiver.pid"
LOG_FILE="${SCRIPT_DIR}/.receiver-supervisor.log"
RESTART_DELAY=5
MAX_RESTART_DELAY=60

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"; }

stop_receiver() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log "Stopping receiver (PID $pid)"
            kill "$pid" 2>/dev/null
            # Wait for graceful shutdown
            for i in $(seq 1 10); do
                kill -0 "$pid" 2>/dev/null || break
                sleep 1
            done
            # Force kill if still alive
            kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null
            log "Receiver stopped"
        fi
        rm -f "$PID_FILE"
    else
        log "No PID file found"
    fi
}

check_status() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Receiver running (PID $pid)"
            curl -s "http://localhost:${CC_RECEIVER_PORT:-2225}" 2>/dev/null | python3 -m json.tool 2>/dev/null || true
            return 0
        else
            echo "PID file exists but process $pid is dead"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "Receiver not running (no PID file)"
        return 1
    fi
}

run_supervised() {
    # Load env
    if [ -f "$ENV_FILE" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +a
    fi

    # Write supervisor PID (the bash process, not python)
    echo $$ > "$PID_FILE"
    trap 'rm -f "$PID_FILE"; log "Supervisor exiting"; exit 0' EXIT INT TERM

    log "Supervisor started (PID $$)"
    log "Receiver port: ${CC_RECEIVER_PORT:-2225}"
    log "Worktree base: ${CC_WORKTREE_BASE:-/home/developer/code/investigations}"

    delay=$RESTART_DELAY

    while true; do
        log "Starting cc_webhook_receiver.py..."

        start_time=$(date +%s)
        python3 "${SCRIPT_DIR}/cc_webhook_receiver.py" 2>&1 | tee -a "$LOG_FILE" || true
        end_time=$(date +%s)
        elapsed=$((end_time - start_time))

        log "Receiver exited after ${elapsed}s"

        # Reset delay if it ran for more than 60s (healthy run)
        if [ "$elapsed" -gt 60 ]; then
            delay=$RESTART_DELAY
        else
            # Exponential backoff on rapid crashes
            delay=$((delay * 2))
            if [ "$delay" -gt "$MAX_RESTART_DELAY" ]; then
                delay=$MAX_RESTART_DELAY
            fi
        fi

        log "Restarting in ${delay}s..."
        sleep "$delay"
    done
}

case "${1:-run}" in
    daemon)
        stop_receiver 2>/dev/null || true
        log "Starting in daemon mode..."
        nohup "$0" run >> "$LOG_FILE" 2>&1 &
        disown
        sleep 2
        check_status
        ;;
    stop)
        stop_receiver
        ;;
    status)
        check_status
        ;;
    run)
        run_supervised
        ;;
    *)
        echo "Usage: $0 {daemon|stop|status|run}"
        exit 1
        ;;
esac

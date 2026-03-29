#!/bin/sh
set -e

# Start Tailscale daemon in userspace networking mode (no root/tun needed)
if [ -n "$TS_AUTHKEY" ]; then
    echo "Starting Tailscale..."
    tailscaled --tun=userspace-networking --state=/tmp/tailscale-state --socket=/tmp/tailscale.sock &
    sleep 2
    if tailscale --socket=/tmp/tailscale.sock up \
        --authkey="$TS_AUTHKEY" \
        --hostname="alert-service" \
        --accept-routes; then
        echo "Tailscale connected"
        if [ -n "$TS_WEBHOOK_TARGET" ]; then
            export CC_WEBHOOK_URL="http://${TS_WEBHOOK_TARGET}:${CC_WEBHOOK_PORT:-2225}"
            echo "CC_WEBHOOK_URL set to $CC_WEBHOOK_URL (via Tailscale)"
        fi
    else
        echo "WARNING: Tailscale failed to connect (bad auth key?). Continuing without mesh."
    fi
else
    echo "TS_AUTHKEY not set, skipping Tailscale"
fi

echo "Starting alert-service..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8011}"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.test.yml"
PROJECT_NAME="${PROJECT_NAME:-wordpress-provenance-clone}"
WP_URL="${WP_URL:-http://localhost:8888}"
WP_TITLE="${WP_TITLE:-Encypher WordPress Review Sandbox}"
WP_ADMIN_USER="${WP_ADMIN_USER:-admin}"
WP_ADMIN_PASSWORD="${WP_ADMIN_PASSWORD:-admin}"
WP_ADMIN_EMAIL="${WP_ADMIN_EMAIL:-admin@example.com}"
API_GATEWAY_BASE="${API_GATEWAY_BASE:-https://api.encypher.com/api/v1}"
WP_API_BASE="${WP_API_BASE:-https://api.encypher.com/api/v1}"
DISPLAY_NAME="${DISPLAY_NAME:-Encypher Review Sandbox}"
DEMO_EMAIL="${DEMO_EMAIL:-wordpress-review-$(date +%s)@example.com}"
DEMO_PASSWORD="${DEMO_PASSWORD:-TestPassword123!}"
KEY_NAME="${KEY_NAME:-wordpress-review-clone}"
DATASET_PATH="${DATASET_PATH:-$ROOT_DIR/plugin/encypher-provenance/data/marketing-blog-posts.json}"
SUMMARY_PATH="${SUMMARY_PATH:-$ROOT_DIR/.wordpress-clone-summary.json}"
# Container name for the Encypher Postgres (auth service database).
# Override if your docker-compose project uses a different name:
#   ENCYPHER_POSTGRES_CONTAINER=my-postgres ./bootstrap_clone_env.sh
ENCYPHER_POSTGRES_CONTAINER="${ENCYPHER_POSTGRES_CONTAINER:-encypher-postgres}"

compose() {
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" "$@"
}

run_wp() {
  compose run --rm wp-cli "$@"
}

wait_for_http() {
  local url="$1"
  local retries="${2:-90}"
  local attempt
  for ((attempt=1; attempt<=retries; attempt++)); do
    if curl -fsS --max-time 3 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  return 1
}

echo "Preflight: checking Enterprise API is reachable..."
# Strip /api/v1 suffix to get base URL, then probe /health
API_BASE_URL="${API_GATEWAY_BASE%/api/v1}"
API_HEALTH_URL="${API_BASE_URL}/health"
if ! curl -fsS --max-time 10 "$API_HEALTH_URL" >/dev/null 2>&1; then
  echo ""
  echo "ERROR: Enterprise API is not reachable at $API_HEALTH_URL"
  echo ""
  echo "The bootstrap requires the main Encypher dev stack to be running."
  echo "Start it first with:"
  echo "  cd <repo-root> && docker compose up -d"
  echo "  # or: uv run --directory enterprise_api uvicorn app.main:app --reload"
  echo ""
  echo "Once the API is healthy, re-run this script."
  exit 1
fi
echo "  -> Enterprise API OK at $API_HEALTH_URL"

if [[ -n "$DEMO_EMAIL" ]] && [[ "${SKIP_ACCOUNT_PROVISION:-}" != "1" ]]; then
  echo "Preflight: checking Postgres container '$ENCYPHER_POSTGRES_CONTAINER' is accessible..."
  if ! docker exec "$ENCYPHER_POSTGRES_CONTAINER" psql -U encypher -d encypher_auth -c "SELECT 1" >/dev/null 2>&1; then
    echo ""
    echo "ERROR: Cannot reach Postgres container '$ENCYPHER_POSTGRES_CONTAINER'."
    echo ""
    echo "This is needed to extract the email verification token for the fresh demo account."
    echo "Options:"
    echo "  1. If using a local dev stack, ensure it is running and set:"
    echo "     ENCYPHER_POSTGRES_CONTAINER=<name> ./bootstrap_clone_env.sh"
    echo "  2. If using the live API with an existing API key, skip account provisioning:"
    echo "     SKIP_ACCOUNT_PROVISION=1 EXISTING_API_KEY=ency_xxx ORG_ID=org_xxx ./bootstrap_clone_env.sh"
    echo ""
    echo "Running containers:"
    docker ps --format "  {{.Names}}" 2>/dev/null || true
    exit 1
  fi
  echo "  -> Postgres container OK"
fi

echo "Preflight: checking port 8888 is available..."
if curl -fsS --max-time 2 "http://localhost:8888" >/dev/null 2>&1; then
  echo "  -> Port 8888 already in use (will be replaced by compose down -v)"
fi

echo "Generating curated 10-post dataset..."
python3 "$ROOT_DIR/generate_marketing_blog_seed.py" --curated --limit 10 --output "$DATASET_PATH"

echo "Resetting isolated WordPress clone stack..."
compose down -v --remove-orphans >/dev/null 2>&1 || true
compose up -d

wait_for_http "$WP_URL" 90

echo "Installing WordPress..."
run_wp core install --url="$WP_URL" --title="$WP_TITLE" --admin_user="$WP_ADMIN_USER" --admin_password="$WP_ADMIN_PASSWORD" --admin_email="$WP_ADMIN_EMAIL" --skip-email >/dev/null
run_wp plugin activate encypher-provenance >/dev/null
run_wp rewrite structure '/%postname%/' --hard >/dev/null
run_wp rewrite flush --hard >/dev/null

echo "Provisioning Encypher demo workspace..."
if [[ "${SKIP_ACCOUNT_PROVISION:-}" == "1" ]]; then
  # Use a pre-existing API key — useful when pointing at the live API.
  # ORG_ID is optional; the plugin auto-discovers it via the connection test.
  if [[ -z "${EXISTING_API_KEY:-}" ]]; then
    echo ""
    echo "ERROR: SKIP_ACCOUNT_PROVISION=1 requires EXISTING_API_KEY to be set."
    echo "  SKIP_ACCOUNT_PROVISION=1 EXISTING_API_KEY=ency_xxx ./bootstrap_clone_env.sh"
    exit 1
  fi
  BOOTSTRAP_JSON="$(python3 -c "
import json, os
print(json.dumps({
  'demo_email': 'n/a (pre-existing account)',
  'demo_password': 'n/a',
  'organization_id': os.environ.get('ORG_ID', ''),
  'organization_name': os.environ.get('DISPLAY_NAME', 'Encypher'),
  'api_key': os.environ['EXISTING_API_KEY'],
  'access_token': '',
}))" EXISTING_API_KEY="$EXISTING_API_KEY" DISPLAY_NAME="$DISPLAY_NAME" ${ORG_ID:+ORG_ID="$ORG_ID"})"
  printf '%s\n' "$BOOTSTRAP_JSON" > "$SUMMARY_PATH"
else

BOOTSTRAP_JSON="$({ API_GATEWAY_BASE="$API_GATEWAY_BASE" DISPLAY_NAME="$DISPLAY_NAME" DEMO_EMAIL="$DEMO_EMAIL" DEMO_PASSWORD="$DEMO_PASSWORD" KEY_NAME="$KEY_NAME" ENCYPHER_POSTGRES_CONTAINER="$ENCYPHER_POSTGRES_CONTAINER" python3 - <<'PY'
import json
import os
import subprocess
import urllib.error
import urllib.request

api_base = os.environ['API_GATEWAY_BASE'].rstrip('/')
display_name = os.environ['DISPLAY_NAME']
demo_email = os.environ['DEMO_EMAIL']
demo_password = os.environ['DEMO_PASSWORD']
key_name = os.environ['KEY_NAME']
postgres_container = os.environ['ENCYPHER_POSTGRES_CONTAINER']
safe_email = demo_email.replace("'", "''")


def request_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', **(headers or {})},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        raise SystemExit(f'{url} -> HTTP {exc.code}: {body}') from exc

signup_response = request_json(
    f'{api_base}/auth/signup',
    {
        'name': 'WordPress Review Demo',
        'email': demo_email,
        'password': demo_password,
    },
)
if not signup_response.get('success'):
    raise SystemExit(f'Unable to create demo user: {signup_response}')

query = (
    "select evt.token "
    "from email_verification_tokens evt "
    "join users u on u.id = evt.user_id "
    f"where u.email = '{safe_email}' and evt.used_at is null "
    "order by evt.created_at desc limit 1;"
)
verification_token = subprocess.check_output(
    [
        'docker',
        'exec',
        postgres_container,
        'psql',
        '-U',
        'encypher',
        '-d',
        'encypher_auth',
        '-Atc',
        query,
    ],
    text=True,
).strip()
if not verification_token:
    raise SystemExit('Unable to resolve verification token for fresh demo user')

verify_response = request_json(
    f'{api_base}/auth/verify-email',
    {'token': verification_token},
)
if not verify_response.get('success'):
    raise SystemExit(f'Unable to verify demo user: {verify_response}')

access_token = verify_response['data']['access_token']
user = verify_response['data']['user']
organization_id = user.get('default_organization_id')
if not organization_id:
    raise SystemExit('Fresh demo user has no default organization')

auth_headers = {'Authorization': f'Bearer {access_token}'}
setup_response = request_json(
    f'{api_base}/auth/setup/complete',
    {
        'account_type': 'organization',
        'display_name': display_name,
        'workflow_category': 'media_publishing',
        'publisher_platform': 'wordpress',
    },
    headers=auth_headers,
)
if not setup_response.get('success'):
    raise SystemExit(f'Unable to complete setup: {setup_response}')

key_response = request_json(
    f'{api_base}/keys/generate',
    {
        'name': key_name,
        'organization_id': organization_id,
        'permissions': ['sign', 'verify', 'read'],
    },
    headers=auth_headers,
)
api_key = key_response.get('key')
if not api_key:
    raise SystemExit(f'Unable to generate API key: {key_response}')

print(json.dumps({
    'demo_email': demo_email,
    'demo_password': demo_password,
    'organization_id': organization_id,
    'organization_name': display_name,
    'api_key': api_key,
    'access_token': access_token,
}))
PY
})"
printf '%s\n' "$BOOTSTRAP_JSON" > "$SUMMARY_PATH"
fi

API_KEY="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["api_key"])' "$SUMMARY_PATH")"
ORG_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["organization_id"])' "$SUMMARY_PATH")"
ORG_NAME="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["organization_name"])' "$SUMMARY_PATH")"

echo "Configuring plugin..."
compose run --rm \
  -e WP_API_BASE="$WP_API_BASE" \
  -e API_KEY="$API_KEY" \
  -e ORG_ID="$ORG_ID" \
  -e ORG_NAME="$ORG_NAME" \
  wp-cli eval '
$settings = get_option("encypher_provenance_settings", []);
if (!is_array($settings)) {
    $settings = [];
}
$settings["api_base_url"] = getenv("WP_API_BASE");
$settings["api_key"] = getenv("API_KEY");
$settings["organization_id"] = getenv("ORG_ID");
$settings["organization_name"] = getenv("ORG_NAME");
$settings["connect_email"] = "";
$settings["connect_session_id"] = "";
$settings["connection_last_status"] = "connected";
$settings["auto_verify"] = true;
$settings["auto_mark_on_publish"] = false;
$settings["auto_mark_on_update"] = false;
$settings["metadata_format"] = "c2pa";
$settings["post_types"] = ["post", "page"];
$settings["badge_position"] = "bottom";
$settings["show_badge"] = true;
update_option("encypher_provenance_settings", $settings);
' >/dev/null

echo "Running connection test..."
compose run --rm wp-cli eval '
$rest = new \EncypherProvenance\Rest();
$request = new WP_REST_Request("POST", "/encypher-provenance/v1/test-connection");
$response = $rest->handle_test_connection_request($request);
if (is_wp_error($response)) {
    fwrite(STDERR, $response->get_error_message() . PHP_EOL);
    exit(1);
}
$data = $response->get_data();
if (($data["status"] ?? "") !== "connected") {
    fwrite(STDERR, "Connection test did not return connected status" . PHP_EOL);
    exit(1);
}
' >/dev/null

echo "Importing sample articles..."
compose exec -T wordpress php /var/www/html/wp-content/plugins/encypher-provenance/import_marketing_blog_posts.php

POST_COUNT="$(compose run --rm wp-cli post list --post_type=post --post_status=publish --format=count)"
# Articles are intentionally left unsigned so they can be signed manually during the demo.
SIGNED_COUNT=0

python3 - <<'PY' "$SUMMARY_PATH" "$WP_URL" "$WP_ADMIN_USER" "$WP_ADMIN_PASSWORD" "$POST_COUNT" "$SIGNED_COUNT"
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
summary = json.loads(summary_path.read_text())
summary.update(
    {
        'wordpress_url': sys.argv[2],
        'wordpress_admin_user': sys.argv[3],
        'wordpress_admin_password': sys.argv[4],
        'post_count': int(sys.argv[5]),
        'signed_post_count': int(sys.argv[6]),
        'dataset_path': 'plugin/encypher-provenance/data/marketing-blog-posts.json',
    }
)
summary_path.write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY

echo "Clone environment ready. Summary written to $SUMMARY_PATH"

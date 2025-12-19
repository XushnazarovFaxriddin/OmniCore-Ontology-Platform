#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_ROOT/infra/podman-compose.yml}"

ACTION="${1:-up}"
shift || true

NO_BUILD=0
TAIL_LINES=200

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-build)
      NO_BUILD=1
      shift
      ;;
    --build)
      NO_BUILD=0
      shift
      ;;
    --tail)
      TAIL_LINES="${2:-200}"
      shift 2
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done
set -- "${POSITIONAL_ARGS[@]}"

load_env() {
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/.env"
    set +a
  fi

  export OMNICORE_BIND_ADDR="${OMNICORE_BIND_ADDR:-0.0.0.0}"
  export OMNICORE_GATEWAY_HOST_PORT="${OMNICORE_GATEWAY_HOST_PORT:-18000}"
  export OMNICORE_DASHBOARD_HOST_PORT="${OMNICORE_DASHBOARD_HOST_PORT:-13000}"

  # Rootless Podman: container root maps to the host user. This avoids bind-mount permission issues.
  export OMNICORE_CONTAINER_USER="${OMNICORE_CONTAINER_USER:-0:0}"

  # Host paths for persistence (override in .env if you want e.g. /mnt/extra/...).
  # If DATABASE_PATH is set (legacy env), use it as OMNICORE_DATA_PATH by default.
  local db_path="${DATABASE_PATH:-}"
  db_path="${db_path%/}"
  local storage_root="$HOME/omnicore"
  if [[ -n "$db_path" ]]; then
    if [[ "$(basename "$db_path")" == "data" ]]; then
      storage_root="$(dirname "$db_path")"
    else
      storage_root="$db_path"
    fi
  fi

  export OMNICORE_DATA_PATH="${OMNICORE_DATA_PATH:-${db_path:-$storage_root/data}}"
  export OMNICORE_LOGS_PATH="${OMNICORE_LOGS_PATH:-$storage_root/logs}"
  export OMNICORE_SNAPSHOTS_PATH="${OMNICORE_SNAPSHOTS_PATH:-$storage_root/snapshots}"
  export OMNICORE_ONTOLOGIES_PATH="${OMNICORE_ONTOLOGIES_PATH:-$storage_root/ontologies}"
  export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"

  mkdir -p "$OMNICORE_DATA_PATH" "$OMNICORE_LOGS_PATH" "$OMNICORE_SNAPSHOTS_PATH" "$OMNICORE_ONTOLOGIES_PATH" "$HF_HOME"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

print_endpoints() {
  echo ""
  echo "Local endpoints:"
  echo "  Gateway:   http://127.0.0.1:${OMNICORE_GATEWAY_HOST_PORT}"
  echo "  Dashboard: http://127.0.0.1:${OMNICORE_DASHBOARD_HOST_PORT}"
  echo ""
  echo "VPN/LAN: use your server IP (e.g., 192.168.1.3):"
  echo "  Gateway:   http://<server-ip>:${OMNICORE_GATEWAY_HOST_PORT}"
  echo "  Dashboard: http://<server-ip>:${OMNICORE_DASHBOARD_HOST_PORT}"
}

wait_for_http() {
  local url="$1"
  local seconds="${2:-60}"
  local start
  start="$(date +%s)"
  while true; do
    if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
      return 0
    fi
    if (( "$(date +%s)" - start >= seconds )); then
      return 1
    fi
    sleep 2
  done
}

wait_for_any_http() {
  local url="$1"
  local seconds="${2:-60}"
  local start
  start="$(date +%s)"
  while true; do
    if curl -sS --max-time 2 "$url" >/dev/null 2>&1; then
      return 0
    fi
    if (( "$(date +%s)" - start >= seconds )); then
      return 1
    fi
    sleep 2
  done
}

case "$ACTION" in
  up|deploy)
    require_cmd podman
    require_cmd podman-compose
    require_cmd curl
    load_env

    if [[ ! -f "$PROJECT_ROOT/src/frontend/omnicloud-ui/package.json" ]]; then
      echo "Frontend not found at: $PROJECT_ROOT/src/frontend/omnicloud-ui/package.json" >&2
      echo "Make sure you cloned the full repo (including the dashboard) before deploying." >&2
      exit 1
    fi

    echo "[1/4] Building backend image (localhost/omnicore:v10)..."
    if [[ "$NO_BUILD" -eq 0 ]]; then
      podman build -t localhost/omnicore:v10 "$PROJECT_ROOT"
    else
      echo "  --no-build set, skipping image build"
    fi

    echo "[2/4] Stopping existing stack (if any)..."
    podman-compose -f "$COMPOSE_FILE" down --remove-orphans || true

    echo "[3/4] Starting stack..."
    podman-compose -f "$COMPOSE_FILE" up -d

    echo "[4/4] Waiting for gateway health..."
    if wait_for_http "http://127.0.0.1:${OMNICORE_GATEWAY_HOST_PORT}/health" 120; then
      echo "Gateway is healthy."
    else
      echo "Gateway did not become healthy in time. Check logs:"
      podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
      echo ""
      podman logs --tail "$TAIL_LINES" omnicore-gateway || true
      exit 1
    fi

    if wait_for_any_http "http://127.0.0.1:${OMNICORE_DASHBOARD_HOST_PORT}" 120; then
      echo "Dashboard is reachable."
    else
      echo "Dashboard is not reachable yet. Check UI logs:"
      podman logs --tail "$TAIL_LINES" omnicore-ui || true
    fi

    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    print_endpoints
    ;;

  down|stop)
    require_cmd podman-compose
    load_env
    podman-compose -f "$COMPOSE_FILE" down --remove-orphans
    ;;

  restart)
    "$0" down
    if [[ "$NO_BUILD" -eq 1 ]]; then
      "$0" up --no-build
    else
      "$0" up
    fi
    ;;

  status)
    require_cmd podman
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    ;;

  logs)
    require_cmd podman
    service="${1:-omnicore-gateway}"
    podman logs -f --tail "$TAIL_LINES" "$service"
    ;;

  *)
    echo "Usage: $0 [up|deploy|down|stop|restart|status|logs] [--no-build] [--tail N]"
    echo ""
    echo "Examples:"
    echo "  $0 up"
    echo "  $0 up --no-build"
    echo "  $0 logs omnicore-gateway --tail 200"
    exit 2
    ;;
esac

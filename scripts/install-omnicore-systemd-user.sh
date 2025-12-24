#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

UNIT_NAME="${UNIT_NAME:-omnicore}"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_PATH="${UNIT_DIR}/${UNIT_NAME}.service"

ACTION="${1:-install}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

install_unit() {
  mkdir -p "$UNIT_DIR"

  cat >"$UNIT_PATH" <<EOF
[Unit]
Description=OmniCore stack (Podman Compose)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
Environment=PODMAN_COMPOSE_BIN=%h/.local/bin/podman-compose
Environment=PATH=%h/.local/bin:%h/.pyenv/shims:%h/.pyenv/bin:/usr/local/bin:/usr/bin:/bin
WorkingDirectory=$PROJECT_ROOT
ExecStart=/usr/bin/env bash $PROJECT_ROOT/scripts/publish-podman.sh up --no-build
ExecStop=/usr/bin/env bash $PROJECT_ROOT/scripts/publish-podman.sh down
RemainAfterExit=yes
TimeoutStartSec=0
TimeoutStopSec=180

[Install]
WantedBy=default.target
EOF

  echo "Installed: $UNIT_PATH"
  echo ""
  echo "Next (recommended):"
  echo "  sudo loginctl enable-linger $USER"
  echo "  systemctl --user daemon-reload"
  echo "  systemctl --user enable --now ${UNIT_NAME}.service"
  echo ""
  echo "Check:"
  echo "  systemctl --user status ${UNIT_NAME}.service"
}

uninstall_unit() {
  if command -v systemctl >/dev/null 2>&1; then
    systemctl --user disable --now "${UNIT_NAME}.service" >/dev/null 2>&1 || true
    systemctl --user daemon-reload >/dev/null 2>&1 || true
  fi

  rm -f "$UNIT_PATH"
  echo "Removed: $UNIT_PATH"
}

case "$ACTION" in
  install)
    install_unit
    ;;
  uninstall)
    uninstall_unit
    ;;
  status)
    require_cmd systemctl
    systemctl --user status "${UNIT_NAME}.service"
    ;;
  *)
    echo "Usage: $0 [install|uninstall|status]" >&2
    exit 2
    ;;
esac

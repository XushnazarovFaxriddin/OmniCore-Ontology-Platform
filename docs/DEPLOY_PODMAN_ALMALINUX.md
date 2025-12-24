# Deploy on AlmaLinux 8.9 with Rootless Podman (VPN-friendly)

This guide is for deploying OmniCore on a shared AlmaLinux 8.9 host using **rootless Podman** and accessing it from a Windows laptop over VPN (e.g. server IP `192.168.1.3`).

## Ports (important)

- **API Gateway**
  - Container port: `8000`
  - Host/VPN port (default): `18000` (`OMNICORE_GATEWAY_HOST_PORT`)
- **Dashboard (Vite)**
  - Container port: `3000`
  - Host/VPN port (default): `13000` (`OMNICORE_DASHBOARD_HOST_PORT`)

From Windows (VPN connected):
- `http://192.168.1.3:18000/docs`
- `http://192.168.1.3:13000`

## 1) Prerequisites

- `podman` 4.x
- `python3.11` + `pip`
- `podman-compose` 1.5+
- `git`, `curl`

If your system `python3` is 3.6 (AlmaLinux default), install Python 3.11 separately and install `podman-compose` with it:

```bash
python3.11 -m pip install --user --upgrade pip podman-compose
~/.local/bin/podman-compose --version
```

## 2) Configure `.env`

Create `.env` in the project root (recommended starting point: `infra/env/.env.example`):

```bash
cp infra/env/.env.example .env
```

Recommended settings for VPN access + port conflicts:

```bash
OMNICORE_BIND_ADDR=0.0.0.0
OMNICORE_GATEWAY_HOST_PORT=18000
OMNICORE_DASHBOARD_HOST_PORT=13000

# Rootless Podman bind-mount permissions
OMNICORE_CONTAINER_USER=0:0
```

Persistence paths (optional, but recommended to use a large shared disk):

```bash
OMNICORE_DATA_PATH=/mnt/extra/omnicore-shared/data
OMNICORE_LOGS_PATH=/mnt/extra/omnicore-shared/logs
OMNICORE_SNAPSHOTS_PATH=/mnt/extra/omnicore-shared/snapshots
OMNICORE_ONTOLOGIES_PATH=/mnt/extra/omnicore-shared/ontologies
```

## 3) Deploy

Use the wrapper script (recommended):

```bash
bash scripts/publish-podman.sh up
```

Skip image rebuild (if you already built it):

```bash
bash scripts/publish-podman.sh up --no-build
```

## 4) Verify locally on the server

```bash
curl -f http://127.0.0.1:18000/health
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## 5) Verify from Windows (VPN)

PowerShell:

```powershell
Test-NetConnection 192.168.1.3 -Port 18000
Test-NetConnection 192.168.1.3 -Port 13000
```

Then open:
- `http://192.168.1.3:18000/docs`
- `http://192.168.1.3:13000`

## 6) Keep it running (recommended for “production”)

On shared/HPC hosts it’s common for user processes to be killed after logout, or for rootless stacks to not restart after reboots.
The most reliable pattern is: **enable linger + run the stack from a systemd user service**.

```bash
# 1) Keep user services running after logout (needs sudo)
sudo loginctl enable-linger "$USER"

# 2) Install the user service unit into ~/.config/systemd/user/
bash scripts/install-omnicore-systemd-user.sh install

# 3) Enable/start it
systemctl --user daemon-reload
systemctl --user enable --now omnicore.service

# 4) Check status
systemctl --user status omnicore.service
```

If your Podman build supports it, also enable automatic restart handling for containers with restart policies:

```bash
systemctl --user enable --now podman-restart.service || true
```

## Troubleshooting

- See what's listening:
  - `ss -ltnp | egrep ':18000|:13000|:18001|:18006'`
- Logs:
  - `podman logs --tail 200 omnicore-roots`
  - `podman logs --tail 200 omnicore-global`
  - `podman logs --tail 200 omnicore-gateway`
  - `podman logs --tail 200 omnicore-ui`
- If `omnicore-ui` logs show `Could not read package.json` (`/app/package.json`): the dashboard folder wasn't mounted. In `infra/podman-compose.yml` the volume must be `../src/frontend/omnicloud-ui:/app:Z`, then redeploy (`bash scripts/publish-podman.sh restart`).
- If you see "Resource limits are not supported...": it's a cgroups v1 rootless warning; safe to ignore (or switch host to cgroups v2).

### Podman lock errors: `acquiring lock ...: file exists`

If `podman ps` prints many errors like:

```
acquiring lock 2 for container ...: file exists
```

Try:

```bash
bash scripts/publish-podman.sh repair
```

Then redeploy:

```bash
bash scripts/publish-podman.sh up --no-build
```

If it still happens frequently on your server, it’s often caused by running rootless Podman state on a network home (NFS/Lustre)
or by user processes being killed abruptly. Two high-impact mitigations:

1) Use the systemd user service section above (linger + systemd).
2) Move Podman storage to a local disk (example):

```bash
mkdir -p /mnt/extra/$USER/podman/{run,graph}
mkdir -p ~/.config/containers
cat > ~/.config/containers/storage.conf <<EOF
[storage]
driver = "overlay"
runroot = "/mnt/extra/$USER/podman/run"
graphroot = "/mnt/extra/$USER/podman/graph"
EOF
```

After changing storage, you must redeploy (images/containers will be recreated in the new storage path).

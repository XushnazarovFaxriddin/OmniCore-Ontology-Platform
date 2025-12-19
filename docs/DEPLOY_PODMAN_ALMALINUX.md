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

## Troubleshooting

- See what’s listening:
  - `ss -ltnp | egrep ':18000|:13000|:18001|:18006'`
- Logs:
  - `podman logs --tail 200 omnicore-roots`
  - `podman logs --tail 200 omnicore-global`
  - `podman logs --tail 200 omnicore-gateway`
  - `podman logs --tail 200 omnicore-ui`
- If you see “Resource limits are not supported…”: it’s a cgroups v1 rootless warning; safe to ignore (or switch host to cgroups v2).


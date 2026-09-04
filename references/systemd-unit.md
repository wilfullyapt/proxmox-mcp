# systemd Unit for Proxmox MCP (LXC Production)

## Unit File: /etc/systemd/system/proxmox-mcp.service

```ini
[Unit]
Description=Stronghold Proxmox MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/proxmox-mcp
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/proxmox-mcp/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

## Setup in LXC

```bash
# After cloning to /opt/proxmox-mcp and setting up venv + .env
sudo cp references/systemd-unit.md /etc/systemd/system/proxmox-mcp.service  # or copy the ini content
sudo systemctl daemon-reload
sudo systemctl enable --now proxmox-mcp
sudo systemctl status proxmox-mcp
```

## Auto-recovery & Update

- `Restart=always` handles crashes/reboots.
- For code update (one-line):
  ```bash
  cd /opt/proxmox-mcp && git pull && sudo systemctl restart proxmox-mcp
  ```
- Or use the helper script (see README).

## Logging

```bash
journalctl -u proxmox-mcp -f
```

## Health Monitoring (optional)

Add a simple watcher or integrate with hermes-monitor for `/health` pings and alerts on failure.
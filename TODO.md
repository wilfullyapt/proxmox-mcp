# Proxmox MCP TODOs — Building Out API-Controlled Systems

This MCP provides repeatable, auditable access to Proxmox systems. Future expansions should stay read-heavy for status/automation while gating write actions.

## High Priority (Core Repeatable Tools)
- [ ] Expand `/resources` with filters (node, type, status) and IP/MAC inventory extraction.
- [ ] `/ceph/*` enhancements: pool status, OSD tree, recovery progress, rebalance planning.
- [ ] `/tasks/recent` + filters (user, type, since, status) + cancellation support for stuck tasks.
- [ ] Node-level: CPU/mem/disk usage, services status, version info.
- [ ] Storage: datastore list, content (ISOs, templates, backups), usage stats.

## Medium Priority (VM/LXC Lifecycle & Power)
- [ ] Full VM/container CRUD helpers (clone from template, resize disk, migrate, snapshot/rollback) — keep behind auth or role checks.
- [ ] Power actions already present; add bulk operations and confirmation for destructive.
- [ ] Network config: bridge/VLAN info per VM, IPAM integration ideas.

## Ceph & Storage Management
- [ ] Pool create/resize/delete (with safety checks).
- [ ] OSD add/remove/maintenance mode.
- [ ] RBD image listing and snapshot management.
- [ ] Backup/restore job status and scheduling hooks.

## SDN & Network
- [ ] SDN zones, VNets, subnets status and config.
- [ ] Firewall rules audit (datacenter + VM level).
- [ ] DNS/DHCP integration points.

## Advanced / Integration
- [ ] `/health/snapshot` enrichment: trend data, alerts on thresholds (integrate with hermes-monitor).
- [ ] Task automation: watch for specific task types and trigger downstream (e.g., post-clone config).
- [ ] Authentication/ACL proxy: expose limited PVE user management for service accounts.
- [ ] Metrics export (Prometheus-compatible) for Ceph, nodes, VMs.
- [ ] Webhook/callback support for long-running tasks.
- [ ] OpenKEEP template extraction: parameterize LXC creation, add example GitHub Actions for deploy.

## Non-Functional
- [ ] Rate limiting + request logging with PII redaction.
- [ ] Comprehensive error mapping from PVE responses.
- [ ] Tests (pytest) for endpoints with mocked PVE.
- [ ] CI: lint, security scan (bandit), build Docker, smoke test.
- [ ] Documentation: OpenAPI enhancements, sequence diagrams for common flows (Ceph recovery, VM provisioning).

## How to Contribute / Build
1. Add endpoint in `main.py` following existing pattern (get_session, try/except → ActionResponse).
2. Document in README + add to health_snapshot if applicable.
3. Update permissions-cheatsheet if new privs needed.
4. Test against real cluster (with read-only token first).
5. Keep philosophy: repeatable & safe; one-off work stays on direct SSH/pct/qm.

Target: make this the canonical, clone-and-run component for any Proxmox homelab/OpenKEEP deployment.
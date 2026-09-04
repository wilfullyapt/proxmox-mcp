"""
Stronghold Proxmox MCP Server — Repeatable tools for Hermes butler.

Self-contained, deployable as LXC or Docker.
Focus: status, reports, queries, routine maintenance (Ceph, cluster, network, tasks).
Finite/one-off work stays on SSH path.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Stronghold Proxmox MCP Server",
    version="0.2.0",
    description="Repeatable tools: cluster status, Ceph, network inventory, tasks, health snapshots."
)

PVE_HOST = os.getenv("PVE_HOST", "https://pve-01:8006")
PVE_TOKEN_ID = os.getenv("PVE_TOKEN_ID")
PVE_TOKEN_SECRET = os.getenv("PVE_TOKEN_SECRET")
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"

if not PVE_TOKEN_ID or not PVE_TOKEN_SECRET:
    print("WARNING: PVE credentials not set in .env")

def get_session():
    sess = requests.Session()
    sess.headers.update({"Authorization": f"PVEAPIToken={PVE_TOKEN_ID}={PVE_TOKEN_SECRET}"})
    if not VERIFY_SSL:
        sess.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return sess

class ActionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0", "pve_host": PVE_HOST}

@app.get("/cluster/status", response_model=ActionResponse)
def cluster_status():
    """Overall cluster status and nodes."""
    try:
        sess = get_session()
        r = sess.get(f"{PVE_HOST}/api2/json/cluster/status")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/nodes", response_model=ActionResponse)
def list_nodes():
    try:
        sess = get_session()
        r = sess.get(f"{PVE_HOST}/api2/json/nodes")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/ceph/status", response_model=ActionResponse)
def ceph_status():
    """Ceph cluster health, OSDs, pools — repeatable status tool."""
    try:
        sess = get_session()
        r = sess.get(f"{PVE_HOST}/api2/json/cluster/ceph/status")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/ceph/osds", response_model=ActionResponse)
def ceph_osds():
    try:
        sess = get_session()
        r = sess.get(f"{PVE_HOST}/api2/json/cluster/ceph/osd")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/resources", response_model=ActionResponse)
def cluster_resources(type: Optional[str] = None):
    """All VMs, containers, storage — use for network IP inventory etc."""
    try:
        sess = get_session()
        url = f"{PVE_HOST}/api2/json/cluster/resources"
        if type:
            url += f"?type={type}"
        r = sess.get(url)
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/tasks/recent", response_model=ActionResponse)
def recent_tasks(limit: int = 20):
    """Recent cluster tasks (maintenance / job history)."""
    try:
        sess = get_session()
        r = sess.get(f"{PVE_HOST}/api2/json/cluster/tasks?limit={limit}")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/health/snapshot", response_model=ActionResponse)
def health_snapshot():
    """Aggregated repeatable health report (nodes + Ceph + basic resources)."""
    try:
        sess = get_session()
        snapshot = {}
        # Nodes
        r = sess.get(f"{PVE_HOST}/api2/json/nodes")
        snapshot["nodes"] = r.json()["data"] if r.ok else {"error": str(r.text)}

        # Ceph
        r = sess.get(f"{PVE_HOST}/api2/json/cluster/ceph/status")
        snapshot["ceph"] = r.json()["data"] if r.ok else {"error": str(r.text)}

        # Resources summary
        r = sess.get(f"{PVE_HOST}/api2/json/cluster/resources")
        snapshot["resources_count"] = len(r.json()["data"]) if r.ok else 0

        return ActionResponse(success=True, data=snapshot)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# Power actions kept for completeness but note: these are repeatable only when scripted
@app.post("/vm/{node}/{vmid}/status/{action}", response_model=ActionResponse)
def vm_action(node: str, vmid: int, action: str):
    valid = {"start", "stop", "reboot", "shutdown"}
    if action not in valid:
        raise HTTPException(400, detail=f"Use one of {valid}")
    try:
        sess = get_session()
        r = sess.post(f"{PVE_HOST}/api2/json/nodes/{node}/qemu/{vmid}/status/{action}")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json().get("data"))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

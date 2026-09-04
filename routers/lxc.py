import os

"""LXC management router (priv-gated creation for reverse proxy etc.)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from logging_config import get_logger
from models import ActionResponse, LXCCreateRequest
from pve_client import get_session

router = APIRouter(prefix="/lxc", tags=["LXC"])


class ReverseProxyTemplate(BaseModel):
    hostname: str = "reverse-proxy"
    ostemplate: str = Field(..., description="Debian 12 standard template path")
    memory: int = 1024
    cores: int = 2
    net0: str = Field("name=eth0,bridge=vmbr0,ip=192.168.0.10/24,gw=192.168.0.1")
    rootfs: str = "local-lvm:20"
    recommended_packages: list[str] = ["caddy", "curl"]
    notes: str = "After creation: install Docker + run Gitea/Registry containers"


@router.post("/create", response_model=ActionResponse)
def create_lxc(req: LXCCreateRequest):
    try:
        sess = get_session()
        params = req.model_dump()
        r = sess.post(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/nodes/{req.node}/lxc", data=params)
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json().get("data"))
    except Exception:
        logger = get_logger()
        logger.exception("PVE API error")
        raise HTTPException(500, detail="Internal server error")


@router.get("/reverse-proxy-template", response_model=ActionResponse)
def reverse_proxy_template(ostemplate: str):
    template = ReverseProxyTemplate(ostemplate=ostemplate)
    return ActionResponse(success=True, data=template.model_dump())


@router.get("/task/{upid}/status", response_model=ActionResponse)
def task_status(node: str, upid: str):
    try:
        sess = get_session()
        r = sess.get(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/nodes/{node}/tasks/{upid}/status")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json().get("data"))
    except Exception:
        logger = get_logger()
        logger.exception("PVE API error")
        raise HTTPException(500, detail="Internal server error")


class ExecRequest(BaseModel):
    node: str
    vmid: int
    command: str = Field(..., description="Command to run inside the LXC")
    confirm: bool = Field(False, description="Must be true to execute")


@router.post("/exec", response_model=ActionResponse)
def lxc_exec(req: ExecRequest):
    if not req.confirm:
        raise HTTPException(400, detail="confirm=True is required for safety")

    try:
        sess = get_session()
        params = {"command": req.command}
        r = sess.post(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/nodes/{req.node}/lxc/{req.vmid}/status/exec", data=params)
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json().get("data"))
    except Exception:
        logger = get_logger()
        logger.exception("PVE API error")
        raise HTTPException(500, detail="Internal server error")

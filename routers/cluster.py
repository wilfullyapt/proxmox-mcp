"""Cluster and node status router."""

import os

from fastapi import APIRouter, HTTPException

from models import ActionResponse
from pve_client import get_session

router = APIRouter(prefix="/cluster", tags=["Cluster"])


@router.get("/status", response_model=ActionResponse)
def cluster_status():
    try:
        sess = get_session()
        r = sess.get(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/cluster/status")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception:
        from logging_config import get_logger
        logger = get_logger()
        logger.exception("Failed to get cluster status")
        raise HTTPException(500, detail="Failed to retrieve cluster status")


@router.get("/nodes", response_model=ActionResponse)
def list_nodes():
    try:
        sess = get_session()
        r = sess.get(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/nodes")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception:
        from logging_config import get_logger
        logger = get_logger()
        logger.exception("Failed to list nodes")
        raise HTTPException(500, detail="Failed to list nodes")


@router.get("/resources", response_model=ActionResponse)
def cluster_resources(type: str = None):
    try:
        sess = get_session()
        url = f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/cluster/resources"
        if type:
            url += f"?type={type}"
        r = sess.get(url)
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception:
        from logging_config import get_logger
        logger = get_logger()
        logger.exception("Failed to get cluster resources")
        raise HTTPException(500, detail="Failed to get resources")

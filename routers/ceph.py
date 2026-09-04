"""Ceph status router."""

import os

from fastapi import APIRouter, HTTPException

from models import ActionResponse
from pve_client import get_session

router = APIRouter(prefix="/ceph", tags=["Ceph"])


@router.get("/status", response_model=ActionResponse)
def ceph_status():
    try:
        sess = get_session()
        r = sess.get(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/cluster/ceph/status")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception:
        from logging_config import get_logger
        logger = get_logger()
        logger.exception("Failed to get Ceph status")
        raise HTTPException(500, detail="Failed to retrieve Ceph status")


@router.get("/osds", response_model=ActionResponse)
def ceph_osds():
    try:
        sess = get_session()
        r = sess.get(f"{os.getenv('PVE_HOST', 'https://pve-01:8006')}/api2/json/cluster/ceph/osd")
        r.raise_for_status()
        return ActionResponse(success=True, data=r.json()["data"])
    except Exception:
        from logging_config import get_logger
        logger = get_logger()
        logger.exception("Failed to get Ceph OSDs")
        raise HTTPException(500, detail="Failed to retrieve Ceph OSDs")

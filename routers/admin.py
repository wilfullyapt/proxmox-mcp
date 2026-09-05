"""Admin / self-maintenance router for the Proxmox MCP.

Provides controlled self-update capability so Hermes can keep the MCP current
without external SSH or direct LXC access.
"""

import os
import subprocess
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from logging_config import get_logger
from models import ActionResponse
from security import get_api_key  # reuses existing API key check when MCP_API_KEY is set

router = APIRouter(prefix="/admin", tags=["Admin / Self-Maintenance"])


class UpdateRequest(BaseModel):
    ref: str = Field(
        default="origin/main",
        description="Git ref to reset to (branch, tag, or commit). Defaults to origin/main."
    )
    force: bool = Field(
        default=False,
        description="If true, run git reset --hard (destructive). Use with caution."
    )


def _run_update(ref: str, force: bool) -> dict:
    """Execute the update logic inside the LXC."""
    logger = get_logger("admin.update")
    logger.info("Starting self-update", ref=ref, force=force)

    try:
        # Change to repo root (assumes running from /opt/proxmox-mcp or similar)
        repo_root = os.getenv("MCP_REPO_ROOT", "/opt/proxmox-mcp")
        os.chdir(repo_root)

        commands = [
            ["git", "fetch", "origin"],
        ]
        if force:
            commands.append(["git", "reset", "--hard", ref])
        else:
            commands.append(["git", "checkout", ref.split("/")[-1] if "/" in ref else ref])
            commands.append(["git", "pull", "--ff-only"])

        commands.append(["pip", "install", "-r", "requirements.txt", "--quiet"])

        output_lines = []
        for cmd in commands:
            logger.info("Running command", cmd=" ".join(cmd))
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            output_lines.append(f"$ {' '.join(cmd)}\n{result.stdout}{result.stderr}")
            if result.returncode != 0:
                logger.error("Command failed", cmd=cmd, returncode=result.returncode)
                return {
                    "success": False,
                    "error": f"Command failed: {' '.join(cmd)}",
                    "output": "\n".join(output_lines),
                }

        # Restart the service (this will kill the current request, which is expected)
        logger.info("Restarting proxmox-mcp service")
        subprocess.Popen(
            ["sudo", "systemctl", "restart", "proxmox-mcp"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return {
            "success": True,
            "message": f"Update to {ref} completed. Service is restarting.",
            "output": "\n".join(output_lines),
        }

    except Exception as exc:
        logger.exception("Self-update failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/update", response_model=ActionResponse)
def trigger_update(
    req: UpdateRequest,
    api_key: Optional[str] = Depends(get_api_key) if os.getenv("MCP_API_KEY") else None,
):
    """
    Trigger a self-update of the MCP.

    Protected by MCP_API_KEY when set. After success the service restarts,
    so callers should poll /health afterwards.
    """
    if os.getenv("MCP_API_KEY") and not api_key:
        raise HTTPException(status_code=401, detail="Valid X-API-Key required")

    result = _run_update(req.ref, req.force)
    return ActionResponse(success=result.get("success", False), data=result)


@router.get("/update/status", response_model=ActionResponse)
def update_status():
    """Lightweight status for polling after an update request."""
    return ActionResponse(
        success=True,
        data={
            "version": os.getenv("MCP_VERSION", "unknown"),
            "repo_root": os.getenv("MCP_REPO_ROOT", "/opt/proxmox-mcp"),
        },
    )

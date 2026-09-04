"""Shared PVE API client (session + helpers)."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

PVE_HOST = os.getenv("PVE_HOST", "https://pve-01:8006")
PVE_TOKEN_ID = os.getenv("PVE_TOKEN_ID")
PVE_TOKEN_SECRET = os.getenv("PVE_TOKEN_SECRET")
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() == "true"


def get_session():
    """Return a requests session authenticated for Proxmox."""
    sess = requests.Session()
    if PVE_TOKEN_ID and PVE_TOKEN_SECRET:
        sess.headers.update({"Authorization": f"PVEAPIToken={PVE_TOKEN_ID}={PVE_TOKEN_SECRET}"})

    if not VERIFY_SSL:
        sess.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    return sess

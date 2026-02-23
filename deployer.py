"""
Netlify Deployer
=================
Pushes the updated events-data.js to your Netlify site using their
Files API — no full rebuild needed, just a single file update.

Required env vars:
    NETLIFY_TOKEN      — your Netlify personal access token
    NETLIFY_SITE_ID    — your site ID (from Netlify dashboard → Site settings)

How it works:
    Netlify's "deploy files" API lets you upload individual files to a
    deploy. We create a new deploy with just events-data.js changed,
    which takes ~2 seconds and doesn't touch any other files.
"""

import os
import hashlib
import json
import requests
from pathlib import Path

NETLIFY_API = "https://api.netlify.com/api/v1"


def deploy_to_netlify(events_js_path: Path) -> str:
    """
    Upload events-data.js to Netlify.
    Returns the deploy URL.
    Raises on failure.
    """
    token   = os.environ.get("NETLIFY_TOKEN")
    site_id = os.environ.get("NETLIFY_SITE_ID")

    if not token:
        raise ValueError("NETLIFY_TOKEN environment variable not set")
    if not site_id:
        raise ValueError("NETLIFY_SITE_ID environment variable not set")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }

    content = events_js_path.read_bytes()
    sha1    = hashlib.sha1(content).hexdigest()

    # ── Step 1: Create a new deploy, declaring which files we're updating ──
    deploy_payload = {
        "files": {
            "/events-data.js": sha1,
        },
        "async": False,
    }

    resp = requests.post(
        f"{NETLIFY_API}/sites/{site_id}/deploys",
        headers=headers,
        json=deploy_payload,
        timeout=30,
    )
    resp.raise_for_status()
    deploy = resp.json()
    deploy_id = deploy["id"]

    required = deploy.get("required", [])

    # ── Step 2: Upload files that Netlify says it needs ──
    if sha1 in required or not required:
        upload_headers = {
            "Authorization":  f"Bearer {token}",
            "Content-Type":   "application/javascript",
        }
        upload_resp = requests.put(
            f"{NETLIFY_API}/deploys/{deploy_id}/files/events-data.js",
            headers=upload_headers,
            data=content,
            timeout=30,
        )
        upload_resp.raise_for_status()

    # ── Step 3: Wait for deploy to be ready ──
    import time
    for _ in range(30):  # wait up to 30s
        status_resp = requests.get(
            f"{NETLIFY_API}/deploys/{deploy_id}",
            headers=headers,
            timeout=10,
        )
        status = status_resp.json().get("state")
        if status == "ready":
            break
        if status == "error":
            raise RuntimeError(f"Netlify deploy errored: {status_resp.json()}")
        time.sleep(1)

    deploy_url = deploy.get("ssl_url") or deploy.get("url", "")
    print(f"  ✓ Netlify deploy {deploy_id} ready: {deploy_url}")
    return deploy_url


def get_current_site_info():
    """Helper to look up your site ID if you don't know it."""
    token = os.environ.get("NETLIFY_TOKEN")
    if not token:
        print("Set NETLIFY_TOKEN first")
        return

    resp = requests.get(
        f"{NETLIFY_API}/sites",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    for site in resp.json():
        print(f"  {site['id']}  {site['name']}  {site.get('ssl_url', '')}")


if __name__ == "__main__":
    # Run this directly to list your sites
    get_current_site_info()

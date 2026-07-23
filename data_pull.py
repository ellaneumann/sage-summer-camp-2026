#!/usr/bin/env python3
"""
w083_bottom_camera_images.py

Pull node W083's BOTTOM camera (imagesampler-bottom) images for the window
2025-06-01 .. 2025-08-31 down to this machine.

W083 == "sage_badriver", Bad River Band of Lake Superior Chippewa, New Odanah
WI (GLIFWC). Its bottom-deck Hanwha XNV-8081Z camera faces the rice
waterway directly, which is why it's the source for Manoomin (wild rice)
work.

Two steps:
  1) Query the SAGE data API (metadata only, no auth) for bottom-camera
     `upload` records and resolve them to JPEG URLs.
  2) Download each JPEG to ./manoomin_w083_bottom/ (needs SAGE_USER /
     SAGE_TOKEN — the storage endpoint is auth-walled even though the
     metadata query isn't).

Uses stdlib only (urllib + curl subprocess) since sage_data_client isn't
installed in this environment and isn't needed for a plain query.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request

DATA_API = "https://data.sagecontinuum.org/api/v1/query"
VSN = "W083"
START = "2025-06-01T00:00:00Z"
END = "2025-08-31T23:59:59Z"
TASK = "imagesampler-bottom"
EXPECTED_CAMERA_TAG = "bottom_camera"
OUT_DIR = "manoomin_w083_bottom"


def load_dotenv(path=".env"):
    """Minimal .env loader: sets SAGE_USER/SAGE_TOKEN from a local, gitignored
    file if present, without overriding already-exported env vars."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


def query_bottom_camera_images():
    """POST to the data API, stream NDJSON, keep only bottom-camera upload
    rows (the ones with a real JPEG URL in `value`)."""
    body = json.dumps({
        "start": START,
        "end": END,
        "filter": {"vsn": VSN, "task": TASK},
    }).encode("utf-8")
    req = urllib.request.Request(
        DATA_API, data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )

    print(f"querying {DATA_API}  vsn={VSN} task={TASK}  {START} .. {END}")
    images = []
    with urllib.request.urlopen(req, timeout=60) as resp:
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("name") != "upload":
                continue
            meta = rec.get("meta", {})
            if meta.get("camera") != EXPECTED_CAMERA_TAG:
                continue
            url = rec.get("value", "")
            if not isinstance(url, str) or "storage.sagecontinuum.org" not in url:
                continue
            images.append({"timestamp": rec.get("timestamp", ""), "url": url})

    print(f"found {len(images)} bottom-camera images")
    return images


def download(url: str, dest: str, sage_user: str, sage_token: str) -> str:
    """curl -fL -u user:token. -L follows the 302 to NRP storage with a
    signed JWT (mandatory); -u is the portal auth (mandatory)."""
    rc = subprocess.run(
        ["curl", "-sS", "-f", "-L", "-u", f"{sage_user}:{sage_token}", url, "-o", dest],
        capture_output=True, text=True,
    )
    if rc.returncode != 0:
        return f"FAIL rc={rc.returncode}: {(rc.stderr or '').strip()[:120]}"
    with open(dest, "rb") as f:
        head = f.read(3)
    if head != b"\xff\xd8\xff":
        return f"FAIL: not a JPEG (magic={head.hex()}) -- auth/NRP issue"
    return f"OK {os.path.getsize(dest):>8d} B"


def download_all(images, out_dir, sage_user, sage_token):
    if not sage_user or not sage_token:
        print("SAGE_USER/SAGE_TOKEN not set -- skipping download.")
        print("Get creds at https://portal.sagecontinuum.org/account/access, then:")
        print("  export SAGE_USER=... SAGE_TOKEN=...")
        print("  python3 w083_bottom_camera_images.py")
        return []

    os.makedirs(out_dir, exist_ok=True)
    fetched = []
    for i, im in enumerate(images, 1):
        tstr = im["timestamp"].split(".")[0].replace("-", "").replace(":", "") + "Z"
        dest = os.path.join(out_dir, f"{VSN}_bottom_{tstr}.jpg")
        status = download(im["url"], dest, sage_user, sage_token)
        print(f"  [{i}/{len(images)}] {os.path.basename(dest)}  {status}")
        if status.startswith("OK"):
            fetched.append(dest)
    return fetched


def main():
    load_dotenv()
    images = query_bottom_camera_images()
    if not images:
        print("No bottom-camera images found for this window.")
        return 0

    ts = [im["timestamp"] for im in images]
    print(f"time range: {min(ts)} .. {max(ts)}")

    fetched = download_all(images, OUT_DIR, os.environ.get("SAGE_USER"), os.environ.get("SAGE_TOKEN"))
    if fetched:
        print(f"\ndownloaded {len(fetched)}/{len(images)} images -> {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

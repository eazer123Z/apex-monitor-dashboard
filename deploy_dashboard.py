#!/usr/bin/env python3
"""deploy_dashboard.py — refresh data.json + redeploy dashboard ke Vercel.

Dipakai oleh cron apex-dashboard-push (tiap 15 menit).
Read-only terhadap trading: hanya baca DB/file lokal, tidak sentuh live/API.
"""
import json
import subprocess
import sys
import os

DASH_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ID = "prj_tgMQCw5ShDAjIwOqgIDhWSZSq2jD"
APEX_DIR = os.path.expanduser("~/workspace/binance-autonomous-quant-v2")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.get("timeout", 120))


def main():
    # 1. Generate fresh data.json via dashboard_data.py (read-only)
    dd = os.path.join(APEX_DIR, "dashboard_data.py")
    out = run([sys.executable, dd], timeout=90)
    if out.returncode != 0:
        print(f"DATA-GEN FAILED: {out.stderr[:500]}")
        return 1
    # validasi JSON sebelum tulis
    json.loads(out.stdout)
    with open(os.path.join(DASH_DIR, "data.json"), "w") as f:
        f.write(out.stdout)
    print(f"data.json refreshed ({len(out.stdout)} bytes)")

    # 2. Read files for deploy
    files = []
    for p in ["index.html", "data.json"]:
        with open(os.path.join(DASH_DIR, p)) as f:
            files.append({"file": p, "data": f.read(), "encoding": "utf-8"})

    # 3. Deploy via vercel MCP
    args = {
        "requestBody": {
            "name": "apex-monitor-dashboard",
            "files": files,
            "project": PROJECT_ID,
            "target": "production",
            "projectSettings": {
                "framework": None,
                "buildCommand": None,
                "outputDirectory": None,
                "installCommand": None,
                "devCommand": None,
            },
        }
    }
    dep = run(["vercel", "call-tool", "--name", "create_deployment",
               "--arguments-json", json.dumps(args)], timeout=120)
    try:
        d = json.loads(dep.stdout)
        t = json.loads(d["result"]["content"][0]["text"])
        url = t["result"]["deployment"]["url"]
        print(f"DEPLOYED: https://{url}")
    except Exception as e:
        print(f"DEPLOY FAILED: {e} | stdout={dep.stdout[:500]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

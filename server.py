#!/usr/bin/env python3
"""
Universal Parks Wait Times Display Box Server
Serves a retro Universal Studios smart-clock display box web app.
Themes: Harry Potter (Wizarding World), MCU (Marvel Super Hero Island), Mario (Super Nintendo World).
Pulls live wait times from queue-times.com with caching.
"""

import http.server
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict

PORT = int(os.environ.get("PORT", 8089))
CACHE_TTL = 60  # Cache wait times for 60 seconds

PARKS = [
    {
        "id": 64,
        "name": "Universal's Islands of Adventure",
        "resort": "Universal Orlando Resort",
        "timezone": "America/New_York",
        "theme_color": "#0284c7",
        "accent_color": "#e23636",
        "icon": "⚡",
        "default_theme": "theme-wizard",
    },
    {
        "id": 65,
        "name": "Universal Studios Florida",
        "resort": "Universal Orlando Resort",
        "timezone": "America/New_York",
        "theme_color": "#d97706",
        "accent_color": "#d4af37",
        "icon": "🎬",
        "default_theme": "theme-wizard",
    },
    {
        "id": 66,
        "name": "Universal Studios Hollywood",
        "resort": "Universal Studios Hollywood",
        "timezone": "America/Los_Angeles",
        "theme_color": "#dc2626",
        "accent_color": "#fbd000",
        "icon": "🍄",
        "default_theme": "theme-mario",
    },
    {
        "id": 284,
        "name": "Universal Studios Japan",
        "resort": "Universal Studios Japan",
        "timezone": "Asia/Tokyo",
        "theme_color": "#e11d48",
        "accent_color": "#00a651",
        "icon": "⭐",
        "default_theme": "theme-mario",
    },
    {
        "id": 334,
        "name": "Universal's Epic Universe",
        "resort": "Universal Orlando Resort",
        "timezone": "America/New_York",
        "theme_color": "#7c3aed",
        "accent_color": "#00f0ff",
        "icon": "🌌",
        "default_theme": "theme-mcu",
    },
    {
        "id": 67,
        "name": "Universal's Volcano Bay",
        "resort": "Universal Orlando Resort",
        "timezone": "America/New_York",
        "theme_color": "#0d9488",
        "accent_color": "#06b6d4",
        "icon": "🌋",
        "default_theme": "theme-classic",
    },
]

# In-memory cache: { park_id: (timestamp, data) }
cache: Dict[int, tuple] = {}


def fetch_park_data(park_id: int) -> Dict[str, Any]:
    now = time.time()
    if park_id in cache:
        cached_time, cached_data = cache[park_id]
        if now - cached_time < CACHE_TTL:
            return cached_data

    url = f"https://queue-times.com/parks/{park_id}/queue_times.json"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        rides = []
        lands = data.get("lands", [])
        for land in lands:
            land_name = land.get("name", "Attractions")
            for r in land.get("rides", []):
                rides.append({
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "land": land_name,
                    "is_open": bool(r.get("is_open", False)),
                    "wait_time": int(r.get("wait_time") or 0),
                    "last_updated": r.get("last_updated"),
                })

        for r in data.get("rides", []):
            rides.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "land": "Attractions",
                "is_open": bool(r.get("is_open", False)),
                "wait_time": int(r.get("wait_time") or 0),
                "last_updated": r.get("last_updated"),
            })

        # Calculate summary statistics
        open_rides = [r for r in rides if r["is_open"]]
        avg_wait = round(sum(r["wait_time"] for r in open_rides) / len(open_rides)) if open_rides else 0
        max_wait = max((r["wait_time"] for r in open_rides), default=0)

        result = {
            "park_id": park_id,
            "rides": rides,
            "total_rides": len(rides),
            "open_rides": len(open_rides),
            "closed_rides": len(rides) - len(open_rides),
            "avg_wait": avg_wait,
            "max_wait": max_wait,
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now)),
        }

        cache[park_id] = (now, result)
        return result

    except Exception as e:
        print(f"Error fetching data for park {park_id}: {e}", file=sys.stderr)
        if park_id in cache:
            # Return stale cache if available
            return cache[park_id][1]
        raise


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/parks":
            self.send_json(200, {"parks": PARKS})
            return

        if path.startswith("/api/parks/") and path.endswith("/waits"):
            try:
                parts = path.strip("/").split("/")
                park_id = int(parts[2])
                data = fetch_park_data(park_id)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return

        if path == "/api/health" or path == "/health":
            self.send_json(200, {"status": "ok", "time": time.time()})
            return

        # Serve index.html or static assets
        if path == "/":
            self.path = "/index.html"

        return super().do_GET()

    def send_json(self, status_code: int, data: Any):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Keep logs clean
        sys.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}\n")


def run():
    ports = [80, 8089]
    env_port = int(os.environ.get("PORT", 0))
    if env_port and env_port not in ports:
        ports.append(env_port)

    servers = []
    for port in ports:
        try:
            httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), RequestHandler)
            servers.append(httpd)
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            print(f"⚡ Universal Wait Times Box Server running on http://0.0.0.0:{port}")
        except Exception as e:
            print(f"Warning: could not bind port {port}: {e}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        for s in servers:
            s.server_close()


if __name__ == "__main__":
    run()

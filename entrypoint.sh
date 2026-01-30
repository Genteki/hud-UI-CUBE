#!/bin/bash
set -e

# Start npm preview server (always needed for navigation tests)
echo "[entrypoint] Starting npm preview server..." >&2
cd /app/uipath_enterprise_benchmark/DeterministicBenchmark
npm run preview -- --host 0.0.0.0 --port 3000 </dev/null >&2 &
NPM_PID=$!

# Start display servers (Xvfb + x11vnc + noVNC) unless explicitly disabled
if [ "${START_DISPLAY_SERVER:-1}" = "1" ]; then
    echo "[entrypoint] Starting display servers (Xvfb + x11vnc + noVNC)..." >&2
    # Ensure Playwright renders to the X display when VNC is enabled
    export PLAYWRIGHT_HEADLESS="0"
    WIDTH="${DISPLAY_WIDTH:-1920}"
    HEIGHT="${DISPLAY_HEIGHT:-1080}"
    Xvfb :1 -screen 0 ${WIDTH}x${HEIGHT}x24 > /dev/null 2>&1 &
    export DISPLAY=:1
    # Start a lightweight desktop session if available (prevents black screen)
    if command -v xfce4-session >/dev/null 2>&1; then
        xfce4-session > /dev/null 2>&1 &
    elif command -v openbox >/dev/null 2>&1; then
        openbox > /dev/null 2>&1 &
    fi
    # Set a background color to make it obvious the display is live
    if command -v xsetroot >/dev/null 2>&1; then
        xsetroot -solid "#2b2b2b" >/dev/null 2>&1 || true
    fi
    x11vnc -display :1 -nopw -listen 0.0.0.0 -forever > /dev/null 2>&1 &
    /usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 > /dev/null 2>&1 &
    sleep 1
else
    echo "[entrypoint] START_DISPLAY_SERVER=0 - skipping display servers" >&2
fi

# Wait for npm server to be ready
echo "[entrypoint] Waiting for preview server to start..." >&2
sleep 3

# Check if npm is still running
if ! kill -0 $NPM_PID 2>/dev/null; then
    echo "[entrypoint] ERROR: npm preview server failed to start" >&2
    exit 1
fi

echo "[entrypoint] Starting MCP server..." >&2
exec python3 -u /app/env.py

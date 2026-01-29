# syntax=docker/dockerfile:1
FROM hudevals/hud-browser-base:latest AS setup

WORKDIR /app

# Stage 1: Install main environment dependencies
COPY pyproject.toml /app/
RUN uv pip install --system --break-system-packages .


# Stage 2: Setup UI_Cube Http Server
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends git nodejs npm xdotool scrot xvfb \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/UiPath/uipath_enterprise_benchmark /app/uipath_enterprise_benchmark
RUN set -e; \
    cd /app/uipath_enterprise_benchmark/DeterministicBenchmark; \
    if [ -f package-lock.json ]; then \
      npm ci --no-audit --no-fund; \
    else \
      npm install --no-audit --no-fund; \
    fi; \
    npm run build

# Stage 3: Copy source code
COPY env.py /app/
COPY tools/ /app/tools/
COPY setup/ /app/setup/
COPY scenarios/ /app/scenarios/
COPY data/ /app/data/
COPY prompts/ /app/prompts/
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh


# Stage 4: Set environment variables
ENV MCP_TRANSPORT="stdio"
ENV HUD_LOG_STREAM="stderr"
ENV PYTHONUNBUFFERED="1"
ENV PYTHONWARNINGS="ignore::SyntaxWarning:pyautogui"
ENV DISPLAY=":1"
ENV PYTHONPATH=/app
ENV FASTMCP_DISABLE_BANNER="1"
# Headless mode - browser runs without display, Xvfb not needed
ENV PLAYWRIGHT_HEADLESS="1"

# Expose ports  
EXPOSE 8000 8080 3000-3200 5000-5200

# Step 5: Entrypoint
# entrypoint.sh starts npm preview server and handles Xvfb based on PLAYWRIGHT_HEADLESS
CMD ["/app/entrypoint.sh"]

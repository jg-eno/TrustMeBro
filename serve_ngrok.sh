#!/usr/bin/env bash
# Terminal 2: tunnel local vLLM (or any service) with ngrok (blocks until Ctrl+C).
# Start ./serve_vllm.sh first (or anything listening on the same port).
# Usage: ./serve_ngrok.sh [port]
# Default port: 8000

set -euo pipefail

PORT="${1:-8000}"

echo "Tunneling http://localhost:${PORT} — ensure vLLM is already listening there."
echo ""

exec ngrok http "${PORT}"

#!/usr/bin/env bash
# Terminal 1: start the OpenAI-compatible vLLM server (blocks until Ctrl+C).
# Usage: ./serve_vllm.sh [model] [port]
# Defaults: model=microsoft/Phi-3-mini-4k-instruct, port=8000

set -euo pipefail

MODEL="${1:-microsoft/Phi-3-mini-4k-instruct}"
PORT="${2:-8000}"

echo "Serving ${MODEL} on 0.0.0.0:${PORT}"
echo "In another terminal, run: ./serve_ngrok.sh ${PORT}"
echo ""

exec vllm serve "${MODEL}" --host 0.0.0.0 --port "${PORT}"

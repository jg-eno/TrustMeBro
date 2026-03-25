# TrustMeBro

## Host and serve the model (vLLM + ngrok)

Use **two terminals**. vLLM must be listening before you start ngrok.

**Terminal 1 — vLLM**

```bash
./serve_vllm.sh
```

Optional: `./serve_vllm.sh "microsoft/Phi-3-mini-4k-instruct" 8000`

**Terminal 2 — ngrok** (same port as vLLM, default `8000`)

```bash
./serve_ngrok.sh
```

Optional: `./serve_ngrok.sh 8000`

The OpenAI-compatible API is at `http://localhost:8000/v1/...` (or your ngrok HTTPS URL).

---

## Run the evaluation app

The evaluator is a FastAPI service that calls your model’s chat endpoint and scores MMLU (`abstract_algebra` validation).

**1. Create a venv and install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Start the API** (default port **8089**)

```bash
source venv/bin/activate
python main.py
```

Or: `uvicorn main:app --host 0.0.0.0 --port 8089`

---

## Call `POST /evaluate` with cURL

Point `api_url` at your vLLM base URL (local or ngrok). Use the same `model_name` vLLM is serving.

**Local vLLM**

```bash
curl -sS -X POST "http://localhost:8089/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "api_url": "http://localhost:8000",
    "model_name": "microsoft/Phi-3-mini-4k-instruct",
    "use_structured_output": true
  }'
```

**Through ngrok** (replace with your tunnel URL)

```bash
curl -sS -X POST "http://localhost:8089/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "api_url": "https://YOUR-SUBDOMAIN.ngrok-free.dev",
    "model_name": "microsoft/Phi-3-mini-4k-instruct",
    "use_structured_output": true
  }'
```

If your inference server does not support structured JSON output, set `"use_structured_output": false`.

The response includes `accuracy` (0–100), `correct`, `total`, and `details` per question.

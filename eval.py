import json
import re
from urllib.parse import urljoin

import httpx
from datasets import load_dataset
from pydantic import ValidationError

from models import MMLUChoice


def _chat_completions_url(api_url: str) -> str:
    base = api_url.rstrip("/") + "/"
    if base.rstrip("/").endswith("chat/completions"):
        return base.rstrip("/")
    return urljoin(base, "v1/chat/completions")


_MMLU_SYSTEM_PROMPT = (
    "You answer multiple-choice questions. "
    "Reply with only the letter of the correct choice (A, B, C, or D). "
    "Do not include explanation unless the user asks for it."
)

_MMLU_SYSTEM_PROMPT_STRUCTURED = (
    "You answer multiple-choice questions. "
    "Respond with JSON only, matching the schema: a single field `letter` that is exactly "
    "one of A, B, C, or D. No other text."
)


def _openai_json_schema_response_format() -> dict:
    """OpenAI Chat Completions `response_format` for strict structured outputs."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "mmlu_choice",
            "strict": True,
            "schema": MMLUChoice.model_json_schema(),
        },
    }


def _mmlu_user_content(question: str, choices: list[str]) -> str:
    lines = [f"Question: {question}", ""]
    for i, c in enumerate(choices):
        lines.append(f"{chr(ord('A') + i)}. {c}")
    return "\n".join(lines)


def _mmlu_messages(question: str, choices: list[str], *, structured: bool) -> list[dict[str, str]]:
    system = _MMLU_SYSTEM_PROMPT_STRUCTURED if structured else _MMLU_SYSTEM_PROMPT
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": _mmlu_user_content(question, choices)},
    ]


def _parse_predicted_index(content: str) -> int | None:
    if not content:
        return None
    t = content.strip()
    m = re.search(r"\b([ABCD])\b", t.upper())
    if m:
        return ord(m.group(1)) - ord("A")
    m = re.search(r"\b([0-3])\b", t)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:answer|choice)\s*[:is]+\s*([ABCD0-3])", t, re.I)
    if m:
        g = m.group(1).upper()
        if g in "ABCD":
            return ord(g) - ord("A")
        return int(g)
    return None


def _letter_to_index(letter: str) -> int:
    return ord(letter.upper()) - ord("A")


def _parse_structured_choice(content: str) -> int | None:
    if not content or not content.strip():
        return None
    try:
        obj = MMLUChoice.model_validate_json(content.strip())
        return _letter_to_index(obj.letter)
    except (ValidationError, json.JSONDecodeError, ValueError):
        return None


def _predicted_index_from_content(content: str, *, structured: bool) -> int | None:
    if structured:
        pred = _parse_structured_choice(content)
        if pred is not None:
            return pred
    return _parse_predicted_index(content)


class EVAL:
    def __init__(self) -> None:
        self.ds = load_dataset("cais/mmlu", "abstract_algebra")

    def evaluation(
        self,
        api_url: str,
        model_name: str,
        *,
        use_structured_output: bool = True,
        timeout_s: float = 120.0,
    ) -> dict:
        val_split = self.ds["validation"]
        url = _chat_completions_url(api_url)
        correct = 0
        details: list[dict] = []

        with httpx.Client(timeout=timeout_s) as client:
            for row in val_split:
                q = row["question"]
                choices = row["choices"]
                gold = int(row["answer"])
                payload: dict = {
                    "model": model_name,
                    "messages": _mmlu_messages(q, choices, structured=use_structured_output),
                }
                if use_structured_output:
                    payload["response_format"] = _openai_json_schema_response_format()
                r = client.post(url, json=payload, headers={"Content-Type": "application/json"})
                r.raise_for_status()
                data = r.json()
                try:
                    content = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError) as e:
                    details.append(
                        {
                            "question": q,
                            "gold_index": gold,
                            "predicted_index": None,
                            "correct": False,
                            "error": f"bad_response: {e}",
                        }
                    )
                    continue

                pred = _predicted_index_from_content(
                    content, structured=use_structured_output
                )
                ok = pred is not None and pred == gold
                if ok:
                    correct += 1
                details.append(
                    {
                        "question": q,
                        "gold_index": gold,
                        "predicted_index": pred,
                        "correct": ok,
                        "raw_reply": content[:500] if content else "",
                    }
                )

        total = len(val_split)
        acc = (100.0 * correct / total) if total else 0.0
        return {
            "accuracy": acc,
            "correct": correct,
            "total": total,
            "details": details,
        }


_eval: EVAL | None = None


def get_eval() -> EVAL:
    global _eval
    if _eval is None:
        _eval = EVAL()
    return _eval

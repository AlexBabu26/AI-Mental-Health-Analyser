"""Services for analysis app - LLM integration and scoring logic."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import requests
from django.conf import settings

from .models import AnalysisStatus, RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class AnalysisPayload:
    stress_score: int
    anxiety_score: int
    depression_score: int
    risk_level: str
    alert_recommended: bool
    rationale_short: str
    ai_message: str
    recommendations: List[str]
    raw_llm_json: str
    analysis_status: str


SYSTEM_PROMPT = """
You are a mental wellness analysis assistant.
You must output ONLY valid JSON. No markdown. No extra text.

Return JSON with EXACT keys:
{
  "stress_score": int (0-10),
  "anxiety_score": int (0-10),
  "depression_score": int (0-10),
  "rationale_short": string (1-2 sentences),
  "ai_message": string (empathetic, supportive, non-judgmental),
  "recommendations": array of 3-6 short strings
}

Important:
- This is not a medical diagnosis.
- Avoid absolute certainty; use cautious language.
""".strip()


def _clamp_int(v: Any, lo: int = 0, hi: int = 10) -> int:
    try:
        n = int(v)
    except Exception:
        n = lo
    return max(lo, min(hi, n))


def _extract_json_from_response(text: str) -> str:
    """
    Extract JSON from response that may contain markdown code blocks or extra text.
    Tries to find JSON object in the response. Handles truncated responses via repair.
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    # Complete JSON object: { ... }
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        extracted = text[start_idx:end_idx + 1]
        try:
            json.loads(extracted)
            return extracted
        except json.JSONDecodeError:
            logger.warning("Failed to parse extracted JSON, attempting repair")
            try:
                from json_repair import repair_json
                return repair_json(extracted)
            except Exception as e:
                logger.error(f"Failed to repair JSON: {e}")
                return extracted
    
    # Truncated or malformed: we have { but no closing } — try repair on from { to end
    if start_idx != -1:
        extracted = text[start_idx:]
        try:
            from json_repair import repair_json
            repaired = repair_json(extracted)
            json.loads(repaired)  # validate
            return repaired
        except Exception:
            pass
    
    return text


def compute_overall(stress: int, anxiety: int, depression: int) -> Decimal:
    avg = (Decimal(stress) + Decimal(anxiety) + Decimal(depression)) / Decimal(3)
    return avg.quantize(Decimal("0.1"))


def risk_from_scores(stress: int, anxiety: int, depression: int, overall: Decimal) -> str:
    if overall >= Decimal("9.0") or depression >= 9:
        return RiskLevel.CRITICAL
    if overall >= Decimal("7.0") or stress >= 8 or anxiety >= 8 or depression >= 8:
        return RiskLevel.HIGH
    if overall >= Decimal("4.0"):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def validate_llm_json(obj: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Returns (normalized_obj, errors)
    """
    errors: List[str] = []

    required = ["stress_score", "anxiety_score", "depression_score", "rationale_short", "ai_message", "recommendations"]
    for k in required:
        if k not in obj:
            errors.append(f"Missing key: {k}")

    stress = _clamp_int(obj.get("stress_score", 0))
    anxiety = _clamp_int(obj.get("anxiety_score", 0))
    depression = _clamp_int(obj.get("depression_score", 0))

    rationale = obj.get("rationale_short", "")
    if not isinstance(rationale, str):
        errors.append("rationale_short must be string")
        rationale = str(rationale)

    ai_message = obj.get("ai_message", "")
    if not isinstance(ai_message, str):
        errors.append("ai_message must be string")
        ai_message = str(ai_message)

    recs = obj.get("recommendations", [])
    if not isinstance(recs, list):
        errors.append("recommendations must be an array")
        recs = []
    else:
        recs = [str(x) for x in recs][:6]
        if len(recs) < 3:
            errors.append("recommendations must have at least 3 items")

    normalized = {
        "stress_score": stress,
        "anxiety_score": anxiety,
        "depression_score": depression,
        "rationale_short": rationale.strip(),
        "ai_message": ai_message.strip(),
        "recommendations": recs,
    }
    return normalized, errors


# -----------------------------
# Provider abstraction
# -----------------------------

class LLMProvider:
    def analyze(self, user_text: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        raise NotImplementedError


class OpenRouterProvider(LLMProvider):
    """
    OpenRouter Chat Completions (OpenAI-compatible).
    Endpoint: POST {base_url}/chat/completions
    Returns the assistant message content (expected to be JSON per SYSTEM_PROMPT).
    """

    def __init__(self) -> None:
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.app_url = settings.OPENROUTER_APP_URL
        self.app_name = settings.OPENROUTER_APP_NAME

    def analyze(self, user_text: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set.")

        url = f"{self.base_url.rstrip('/')}/chat/completions"

        messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Optional prior context messages in OpenAI format:
        # context=[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]
        if context:
            for m in context[-10:]:
                role = m.get("role")
                content = m.get("content")
                if role in ("user", "assistant") and isinstance(content, str):
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_text})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Recommended attribution headers:
            # "HTTP-Referer": self.app_url,
            # "X-Title": self.app_name,
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            error_text = resp.text[:500] if hasattr(resp, 'text') else str(resp.status_code)
            logger.error(f"OpenRouter API error {resp.status_code}: {error_text}")
            raise RuntimeError(f"OpenRouter error {resp.status_code}: {error_text}")

        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
            # Extract JSON from response if wrapped in markdown or extra text
            content = _extract_json_from_response(content)
            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected OpenRouter response format: {json.dumps(data)[:500]}")
            raise RuntimeError(f"Unexpected OpenRouter response shape: {str(e)}")


class StubProvider(LLMProvider):
    def analyze(self, user_text: str, context: Optional[List[Dict[str, str]]] = None) -> str:
        # Keep stub as fallback for development
        return json.dumps(
            {
                "stress_score": 3,
                "anxiety_score": 3,
                "depression_score": 2,
                "rationale_short": "Stub output for development.",
                "ai_message": "Thanks for sharing. Tell me a bit more about what's been on your mind.",
                "recommendations": [
                    "Take a short breathing break.",
                    "Write down one next step you can take today.",
                    "Consider speaking with someone you trust if it helps.",
                ],
            }
        )


def get_provider() -> LLMProvider:
    provider = (getattr(settings, "LLM_PROVIDER", "stub") or "stub").lower()
    if provider == "openrouter":
        return OpenRouterProvider()
    return StubProvider()


def analyze_text(user_text: str, context: Optional[List[Dict[str, str]]] = None) -> AnalysisPayload:
    """
    1) call LLM provider
    2) parse JSON
    3) validate schema
    4) compute risk + alert flag deterministically
    """
    # Input validation
    if not user_text or not user_text.strip():
        logger.warning("Empty user text provided to analyze_text")
        return AnalysisPayload(
            stress_score=0,
            anxiety_score=0,
            depression_score=0,
            risk_level=RiskLevel.LOW,
            alert_recommended=False,
            rationale_short="No text provided for analysis.",
            ai_message="Please share what's on your mind.",
            recommendations=["Try writing a message about how you're feeling."],
            raw_llm_json="",
            analysis_status=AnalysisStatus.FAILED,
        )
    
    user_text = user_text.strip()[:8000]  # Enforce max length
    
    provider = get_provider()

    try:
        raw = provider.analyze(user_text=user_text, context=context)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            try:
                from json_repair import repair_json
                raw = repair_json(raw)
                obj = json.loads(raw)
            except Exception as repair_err:
                logger.error(f"JSON decode error from LLM (repair failed): {raw[:500]} ... {repair_err}")
                raise json.JSONDecodeError("LLM returned invalid/truncated JSON", raw, 0)
    except json.JSONDecodeError:
        logger.error(f"JSON decode error from LLM: {raw[:500]}")
        return AnalysisPayload(
            stress_score=0,
            anxiety_score=0,
            depression_score=0,
            risk_level=RiskLevel.LOW,
            alert_recommended=False,
            rationale_short="Analysis failed due to invalid response format.",
            ai_message="I had trouble processing that message. Please try again.",
            recommendations=[
                "Try rephrasing your message.",
                "Keep it short and specific.",
                "If urgent, contact a professional.",
            ],
            raw_llm_json=raw[:1000],  # Limit stored error text
            analysis_status=AnalysisStatus.FAILED,
        )
    except Exception as exc:
        logger.error(f"LLM provider error: {str(exc)}", exc_info=True)
        return AnalysisPayload(
            stress_score=0,
            anxiety_score=0,
            depression_score=0,
            risk_level=RiskLevel.LOW,
            alert_recommended=False,
            rationale_short="Analysis failed due to provider error.",
            ai_message="I had trouble analyzing that message. Please try again.",
            recommendations=[
                "Try rephrasing your message.",
                "Keep it short and specific.",
                "If urgent, contact a professional.",
            ],
            raw_llm_json=str(exc)[:1000],  # Limit stored error text
            analysis_status=AnalysisStatus.FAILED,
        )

    normalized, errors = validate_llm_json(obj)
    stress = normalized["stress_score"]
    anxiety = normalized["anxiety_score"]
    depression = normalized["depression_score"]

    overall = compute_overall(stress, anxiety, depression)
    risk = risk_from_scores(stress, anxiety, depression, overall)
    alert_recommended = risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    status = AnalysisStatus.OK if not errors else AnalysisStatus.REPAIRED

    # Even if "repaired", we still used normalized safe values.
    return AnalysisPayload(
        stress_score=stress,
        anxiety_score=anxiety,
        depression_score=depression,
        risk_level=risk,
        alert_recommended=alert_recommended,
        rationale_short=normalized["rationale_short"],
        ai_message=normalized["ai_message"],
        recommendations=normalized["recommendations"],
        raw_llm_json=raw,
        analysis_status=status,
    )

"""LLM Provider Adapter interface and implementations (Groq, OpenAI, Gemini, Anthropic, Heuristic Fallback)."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """Abstract adapter interface for LLM-assisted evaluation and narrative reasoning."""

    @abstractmethod
    def generate_narrative_reason(
        self,
        candidate_name: str,
        eligible: bool,
        total_score: float,
        breakdown_dict: Dict[str, float],
        strengths: List[str],
        concerns: List[str],
        rejection_reasons: List[str],
        matched_skills: List[str],
        github_summary: str,
    ) -> str:
        """Generate an explainable 50 to 100 word evaluation justification."""
        pass


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI API adapter using standard HTTP completions endpoint."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate_narrative_reason(
        self,
        candidate_name: str,
        eligible: bool,
        total_score: float,
        breakdown_dict: Dict[str, float],
        strengths: List[str],
        concerns: List[str],
        rejection_reasons: List[str],
        matched_skills: List[str],
        github_summary: str,
    ) -> str:
        prompt = (
            f"Write a concise, professional 50 to 100 word evaluation summary for candidate '{candidate_name}'.\n"
            f"Eligible: {eligible}\n"
            f"Score: {total_score}/100\n"
            f"Breakdown: {breakdown_dict}\n"
            f"Rejection Reasons: {rejection_reasons}\n"
            f"Strengths: {strengths}\n"
            f"Concerns: {concerns}\n"
            f"Skills: {matched_skills}\n"
            f"GitHub: {github_summary}\n"
            "Requirements: The output MUST be between 50 and 100 words. Explain specific evidence or why rejected."
        )

        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a senior tech lead screening SDE AI internship candidates. Write concise, exact 50-100 word evaluations."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 180,
                    }
                )
                if resp.status_code == 200:
                    text = resp.json()["choices"][0]["message"]["content"].strip()
                    # Verify length
                    words = text.split()
                    if 40 <= len(words) <= 120:
                        return text
        except Exception as e:
            logger.warning(f"OpenAI API call failed, falling back to heuristic engine: {e}")

        # Fallback if call fails
        return HeuristicAdapter().generate_narrative_reason(
            candidate_name, eligible, total_score, breakdown_dict, strengths,
            concerns, rejection_reasons, matched_skills, github_summary
        )


class GroqAdapter(OpenAIAdapter):
    """Groq API adapter (OpenAI-compatible /chat/completions). Supports Qwen, Llama, etc."""

    def __init__(self, api_key: str, model: str = "qwen/qwen3.8-27b", base_url: str = "https://api.groq.com/openai/v1"):
        super().__init__(api_key=api_key, model=model, base_url=base_url)


class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini API adapter via HTTP."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model

    def generate_narrative_reason(
        self,
        candidate_name: str,
        eligible: bool,
        total_score: float,
        breakdown_dict: Dict[str, float],
        strengths: List[str],
        concerns: List[str],
        rejection_reasons: List[str],
        matched_skills: List[str],
        github_summary: str,
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            f"Write a concise, professional 50 to 100 word evaluation summary for candidate '{candidate_name}'.\n"
            f"Eligible: {eligible}\n"
            f"Score: {total_score}/100\n"
            f"Breakdown: {breakdown_dict}\n"
            f"Rejection Reasons: {rejection_reasons}\n"
            f"Strengths: {strengths}\n"
            f"Concerns: {concerns}\n"
            f"Skills: {matched_skills}\n"
            f"GitHub: {github_summary}\n"
            "Requirements: The output MUST be between 50 and 100 words. Explain specific evidence or why rejected."
        )

        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(
                    url,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    headers={"Content-Type": "application/json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    words = text.split()
                    if 40 <= len(words) <= 120:
                        return text
        except Exception as e:
            logger.warning(f"Gemini API call failed, falling back to heuristic engine: {e}")

        return HeuristicAdapter().generate_narrative_reason(
            candidate_name, eligible, total_score, breakdown_dict, strengths,
            concerns, rejection_reasons, matched_skills, github_summary
        )


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic Messages API adapter (Claude models)."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest", base_url: str = "https://api.anthropic.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate_narrative_reason(
        self,
        candidate_name: str,
        eligible: bool,
        total_score: float,
        breakdown_dict: Dict[str, float],
        strengths: List[str],
        concerns: List[str],
        rejection_reasons: List[str],
        matched_skills: List[str],
        github_summary: str,
    ) -> str:
        prompt = (
            f"Write a concise, professional 50 to 100 word evaluation summary for candidate '{candidate_name}'.\n"
            f"Eligible: {eligible}\n"
            f"Score: {total_score}/100\n"
            f"Breakdown: {breakdown_dict}\n"
            f"Rejection Reasons: {rejection_reasons}\n"
            f"Strengths: {strengths}\n"
            f"Concerns: {concerns}\n"
            f"Skills: {matched_skills}\n"
            f"GitHub: {github_summary}\n"
            "Requirements: The output MUST be between 50 and 100 words. Explain specific evidence or why rejected."
        )
        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 250,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    blocks = data.get("content", [])
                    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
                    if text and 40 <= len(text.split()) <= 120:
                        return text
        except Exception as e:
            logger.warning(f"Anthropic API call failed, falling back to heuristic engine: {e}")

        return HeuristicAdapter().generate_narrative_reason(
            candidate_name, eligible, total_score, breakdown_dict, strengths,
            concerns, rejection_reasons, matched_skills, github_summary
        )


class HeuristicAdapter(BaseLLMAdapter):
    """
    Deterministic rule-based reasoning engine ensuring guaranteed 50-100 word
    explanations with zero external API dependencies or network latency.
    """

    def generate_narrative_reason(
        self,
        candidate_name: str,
        eligible: bool,
        total_score: float,
        breakdown_dict: Dict[str, float],
        strengths: List[str],
        concerns: List[str],
        rejection_reasons: List[str],
        matched_skills: List[str],
        github_summary: str,
    ) -> str:
        if not eligible:
            # Generate 50-100 word rejection explanation
            reasons_text = ", ".join(rejection_reasons)
            skills_text = ", ".join(matched_skills[:4]) if matched_skills else "general software development"
            
            p1 = (
                f"{candidate_name} was marked ineligible during screening due to {reasons_text.lower()}. "
                f"While the candidate presents background in {skills_text}, the profile lacks practical evidence "
                f"of Python backend development and demonstrable exposure to agentic, RAG, or LLM-based workflows. "
            )
            p2 = (
                f"For this SDE internship, candidates must demonstrate functional experience building with Python services "
                f"alongside agent orchestration, tool calling, or vector retrieval pipelines. "
                f"Consequently, this profile does not meet the mandatory baseline criteria for further scoring consideration."
            )
            full = f"{p1}{p2}".strip()
            return self._ensure_word_count(full, 55, 95)

        # Eligible candidate 50-100 word justification
        s_text = ", ".join(strengths[:2]) if strengths else "Python backend development"
        c_text = concerns[0] if concerns else "No significant technical weaknesses observed"
        skills_str = ", ".join(matched_skills[:5])

        p1 = (
            f"{candidate_name} qualifies as an eligible candidate with a total score of {total_score:.1f}/100. "
            f"The candidate demonstrates practical engineering capability highlighted by {s_text.lower()}, "
            f"supported by core stack competencies in {skills_str}. "
        )
        p2 = (
            f"GitHub enrichment indicates: {github_summary} "
            f"Primary area for review: {c_text}. "
            f"Overall, this profile exhibits solid engineering depth and the requisite hands-on exposure "
            f"to modern agentic systems to succeed in the SDE AI internship."
        )
        full = f"{p1}{p2}".strip()
        return self._ensure_word_count(full, 55, 95)

    @staticmethod
    def _ensure_word_count(text: str, min_words: int, max_words: int) -> str:
        """Trim or pad text gracefully to remain between min_words and max_words."""
        words = text.split()
        if len(words) > max_words:
            # Cut at last period before max_words
            truncated = " ".join(words[:max_words])
            last_dot = truncated.rfind(".")
            if last_dot > 200:
                return truncated[:last_dot + 1]
            return truncated + "."
        elif len(words) < min_words:
            padding = " Demonstrates clear relevance to the engineering requirements."
            text += padding
        return text


def get_llm_adapter() -> BaseLLMAdapter:
    """Factory to retrieve configured LLM adapter with automatic fallback."""
    provider = settings.LLM_PROVIDER.lower()

    if provider == "groq":
        if settings.GROQ_API_KEY:
            return GroqAdapter(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL,
                base_url=settings.GROQ_BASE_URL,
            )
        return HeuristicAdapter()

    if provider == "openai" or (provider == "auto" and settings.OPENAI_API_KEY):
        if settings.OPENAI_API_KEY:
            return OpenAIAdapter(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL,
            )

    if provider == "gemini" or (provider == "auto" and settings.GEMINI_API_KEY):
        if settings.GEMINI_API_KEY:
            return GeminiAdapter(
                api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL,
            )

    if provider == "anthropic" or (provider == "auto" and settings.ANTHROPIC_API_KEY):
        if settings.ANTHROPIC_API_KEY:
            return AnthropicAdapter(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL,
                base_url=settings.ANTHROPIC_BASE_URL,
            )

    if provider == "auto" and settings.GROQ_API_KEY:
        return GroqAdapter(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            base_url=settings.GROQ_BASE_URL,
        )

    return HeuristicAdapter()

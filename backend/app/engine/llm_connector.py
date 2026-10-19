import re
import logging
from typing import Dict, Any, List, Optional, Tuple
import httpx

from app.config import settings
from app.compliance.phi_scrubber import phi_scrubber

logger = logging.getLogger("medguard.engine.llm_connector")


class HybridLLMConnector:
    """
    Production-grade Hybrid Cloud LLM & Local Clinical Intelligence Connector.
    Combines:
    1. Strict Pre-Transmission HIPAA Safe Harbor & Sinhala/Singlish PHI Scrubbing
    2. Colloquial, Singlish (Romanized Sinhala), and Misspelled Narrative NLU Normalization
    3. Multi-Provider Live Cloud LLM Synthesis (Google Gemini 1.5 Pro, Claude 3.5 Sonnet, OpenAI GPT-4o)
    4. Post-Inference Clinical Safety Guardrail Verification
    5. Zero-Downtime Automatic Fallback to the 100% Local Deterministic Clinical Engine
    """

    # Colloquial, Singlish (Romanized Sinhala), and Misspelled Medical Token Normalization Map
    COLLOQUIAL_AND_SINGLISH_LEXICON: List[Tuple[str, str]] = [
        # Romanized Sinhala (Singlish) Emergency & Symptom Phrases
        (r"\bpapuw(e|a)\s+(thada\s+)?(kakkuma|wedanawa|hirawima|pain)\b", "severe chest pain tightness pressure"),
        (r"\bpapuw(e|a)\b", "chest"),
        (r"\bwam\s+ath(a|ata)\b", "left arm radiating"),
        (r"\bhusma\s+ganna\s+(amarui|ba|bari|apahasui)\b", "severe shortness of breath dyspnea cannot breathe"),
        (r"\bhusma\b", "breathing dyspnea respiratory"),
        (r"\b(oluw(e|a)|his(e|a))\s+(kakkuma|wedanawa|ridenawa)\b", "headache head pain cephalalgia"),
        (r"\bthada\s+una\b", "high grade fever pyrexia"),
        (r"\buna\b", "fever pyrexia"),
        (r"\bwaman(e|aya)\b", "vomiting nausea emesis"),
        (r"\bokkaraya\b", "nausea"),
        (r"\bkarakilla\b", "dizziness vertigo lightheadedness"),
        (r"\bklanthaya\b", "syncope fainted dizziness"),
        (r"\bsi(ni|nee)\s+(wadi|adu)\b", "blood sugar glucose diabetes glycemic"),
        (r"\bdiyawadiyawa\b", "diabetes type 2 glycemic"),
        (r"\b(bada|bade)\s+(kakkuma|wedanawa|ridenawa|dawilla)\b", "abdominal stomach pain epigastric burning"),
        (r"\bkassa\b", "cough pulmonary bronchitis"),
        (r"\bdadiya\b", "sweating diaphoresis"),
        (r"\bdawas\s*(\d+)\b", r"\1 days onset"),
        (r"\bpaya\s*(\d+)\b", r"\1 hours sudden onset"),
        (r"\bsathi\s*(\d+)\b", r"\1 weeks duration"),

        # Common English Clinical Typos & Misspellings in Patient Narratives
        (r"\b(cheast|chst)\s*(pane|pain|pains|preasure|presure)\b", "chest pain pressure"),
        (r"\b(radieting|radating|spreding)\b", "radiating spreading"),
        (r"\b(sweting|sweeting)\b", "sweating diaphoresis"),
        (r"\b(hedache|headach|headahe|migrane)\b", "headache migraine"),
        (r"\b(brething|breatheing|breathng)\b", "breathing dyspnea"),
        (r"\b(vomting|vomitting|nausia|nauseous)\b", "vomiting nausea"),
        (r"\b(dizzyness|dizzines)\b", "dizziness"),
        (r"\b(stomac|stomache|abdomnal)\b", "stomach abdominal"),
        (r"\b(diabetis|diabtes|shugr)\b", "diabetes blood sugar"),
        (r"\b(paralisis|numbnes|weaknes)\b", "paralysis numbness weakness"),
        (r"\b(fevar|feaver)\b", "fever"),
    ]

    FORBIDDEN_UNSAFE_PATTERNS = [
        "i diagnose you with",
        "you definitely have",
        "stop taking your prescribed",
        "discontinue your insulin immediately",
        "take 325mg aspirin immediately",
        "inject 10 units of insulin",
        "take 500mg amoxicillin"
    ]

    CLINICAL_SYSTEM_PROMPT = (
        "You are MedGuard AI, a HIPAA/GDPR-compliant, evidence-grounded Clinical Decision Support "
        "and Patient Triage Assistant inspired by NHS Digital and Epic Systems.\n"
        "CRITICAL CLINICAL SAFETY RULES:\n"
        "1. NEVER formulate definitive unverified medical diagnoses or prescribe unauthorized medication dosages. "
        "Always use probabilistic clinical terminology ('Reported presentation may correlate with...', "
        "'Clinical differential considerations include...').\n"
        "2. Ground EVERY clinical statement strictly in the provided institutional guideline chunks and WHO ICD-11 ontology context.\n"
        "3. Cite the provided evidence chunks inline using bracketed numeric badges exactly as `[Ref 1]`, `[Ref 2]`, etc.\n"
        "4. Understand complex, colloquial, grammatically imperfect, Sinhala, Singlish, or English patient narratives with high clinical empathy.\n"
        "5. Always conclude with explicit red-flag safety-netting instructions (including Sri Lanka 1990 Suwa Seriya / 911 / 999 for acute emergencies).\n"
        "6. Respond in the requested language (Sinhala `si` or English `en`)."
    )

    def __init__(self):
        # Runtime overrides allow configuring provider/keys dynamically without server restart
        self._runtime_provider: Optional[str] = None
        self._runtime_keys: Dict[str, str] = {}
        self._runtime_models: Dict[str, str] = {}

    def configure_runtime(
        self,
        provider: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        gemini_model: Optional[str] = None,
        anthropic_model: Optional[str] = None,
        openai_model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates runtime provider and API keys in memory for immediate hybrid switching."""
        if provider is not None:
            self._runtime_provider = provider.lower().strip()
        if gemini_api_key is not None:
            self._runtime_keys["gemini"] = gemini_api_key.strip()
        if anthropic_api_key is not None:
            self._runtime_keys["anthropic"] = anthropic_api_key.strip()
        if openai_api_key is not None:
            self._runtime_keys["openai"] = openai_api_key.strip()
        if gemini_model:
            self._runtime_models["gemini"] = gemini_model.strip()
        if anthropic_model:
            self._runtime_models["anthropic"] = anthropic_model.strip()
        if openai_model:
            self._runtime_models["openai"] = openai_model.strip()
        return self.get_status()

    def _get_api_key(self, provider: str) -> str:
        if provider in self._runtime_keys and self._runtime_keys[provider]:
            return self._runtime_keys[provider]
        if provider == "gemini":
            return settings.GEMINI_API_KEY
        if provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        if provider == "openai":
            return settings.OPENAI_API_KEY
        return ""

    def _get_model(self, provider: str) -> str:
        if provider in self._runtime_models and self._runtime_models[provider]:
            return self._runtime_models[provider]
        if provider == "gemini":
            return settings.GEMINI_MODEL
        if provider == "anthropic":
            return settings.ANTHROPIC_MODEL
        if provider == "openai":
            return settings.OPENAI_MODEL
        return "local-deterministic-v1"

    def resolve_active_provider(self) -> Tuple[str, str]:
        """
        Determines which LLM provider is currently active.
        Returns (provider_name, model_name).
        If 'auto', selects the first configured cloud provider (Gemini -> Claude -> OpenAI),
        or falls back to 'local' deterministic mode if no cloud API key is present.
        """
        configured = (self._runtime_provider or settings.LLM_PROVIDER or "auto").lower().strip()

        if configured == "local":
            return "local", "MedGuard-Local-Deterministic-RAG"

        if configured in ("gemini", "anthropic", "openai"):
            if self._get_api_key(configured):
                return configured, self._get_model(configured)
            return "local", "MedGuard-Local-Deterministic-RAG (Fallback: Missing API Key)"

        # Auto mode: check Gemini -> Anthropic -> OpenAI
        for candidate in ("gemini", "anthropic", "openai"):
            if self._get_api_key(candidate):
                return candidate, self._get_model(candidate)

        return "local", "MedGuard-Local-Deterministic-RAG"

    def get_status(self) -> Dict[str, Any]:
        """Returns current Hybrid LLM Connector status without exposing raw secret keys."""
        active_provider, active_model = self.resolve_active_provider()
        return {
            "configured_mode": self._runtime_provider or settings.LLM_PROVIDER,
            "active_provider": active_provider,
            "active_model": active_model,
            "cloud_llm_enabled": active_provider in ("gemini", "anthropic", "openai"),
            "phi_scrubber_enforced_pre_cloud": True,
            "deterministic_red_flag_gate_active": True,
            "providers_configured": {
                "gemini": bool(self._get_api_key("gemini")),
                "anthropic": bool(self._get_api_key("anthropic")),
                "openai": bool(self._get_api_key("openai")),
                "local_fallback": True
            },
            "models": {
                "gemini": self._get_model("gemini"),
                "anthropic": self._get_model("anthropic"),
                "openai": self._get_model("openai")
            }
        }

    def normalize_complex_patient_narrative(self, raw_narrative: str) -> Dict[str, Any]:
        """
        Pre-processes complex, ungrammatical, colloquial, Singlish (Romanized Sinhala),
        or misspelled patient narratives into normalized clinical search tokens while
        scrubbing all HIPAA Safe Harbor + Sinhala/Singlish PHI identifiers first.
        """
        if not raw_narrative:
            return {
                "redacted_text": "",
                "normalized_clinical_query": "",
                "scrubbed_entities": [],
                "expanded_terms": []
            }

        # 1. Always scrub PHI before any processing or external transmission
        redacted_text, scrubbed_entities = phi_scrubber.redact(raw_narrative)

        # 2. Expand colloquialisms, Singlish medical phrases, and common typos
        normalized = redacted_text
        expanded_terms: List[str] = []

        for pattern, replacement in self.COLLOQUIAL_AND_SINGLISH_LEXICON:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
                expanded_terms.append(replacement)

        # Collapse noisy punctuation/whitespace from long run-on sentences
        cleaned_query = re.sub(r"\s+", " ", normalized).strip()
        if expanded_terms:
            cleaned_query = f"{redacted_text} {' '.join(expanded_terms)}"

        return {
            "redacted_text": redacted_text,
            "normalized_clinical_query": cleaned_query,
            "scrubbed_entities": scrubbed_entities,
            "expanded_terms": expanded_terms
        }

    def scrub_conversation_history(
        self,
        history: Optional[List[Dict[str, str]]]
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """Scrubs all conversation history messages of PHI before sending to a Cloud LLM."""
        if not history:
            return [], []

        scrubbed_history: List[Dict[str, str]] = []
        all_entities = set()
        for turn in history[-6:]:  # Keep recent 6 turns for clinical context window
            role = turn.get("role", "user")
            content = turn.get("content", "")
            clean_content, entities = phi_scrubber.redact(content)
            all_entities.update(entities)
            scrubbed_history.append({"role": role, "content": clean_content})

        return scrubbed_history, sorted(list(all_entities))

    def _build_grounded_prompt(
        self,
        redacted_query: str,
        normalized_query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en",
        workflow_state: str = "STRUCTURED_ASSESSMENT",
        intake_questions: Optional[List[str]] = None,
        differentials: Optional[List[Dict[str, Any]]] = None,
        age_group: str = "ADULT",
        biological_sex: str = "UNSPECIFIED"
    ) -> str:
        lang_instruction = (
            "Respond entirely in clear, empathetic, natural, and medically accurate Sinhala (සිංහල), "
            "preserving English medical codes (e.g., ICD-11 codes) and citation tags ([Ref 1], [Ref 2])."
            if language == "si"
            else "Respond in clear, empathetic, professional clinical English, preserving inline citation tags ([Ref 1], [Ref 2])."
        )

        evidence_block = []
        for idx, chunk in enumerate(context_chunks):
            ref_tag = f"[Ref {idx + 1}]"
            title = chunk.get("source_title") or chunk.get("section_header") or "Clinical Guideline"
            domain = chunk.get("clinical_domain", "Clinical Medicine")
            authority = chunk.get("issuing_authority") or chunk.get("metadata", {}).get("source", "WHO / NICE")
            snippet = chunk.get("text_content", "")
            evidence_block.append(f"{ref_tag} ({authority} - {title} | {domain}):\n{snippet}")

        evidence_str = "\n\n".join(evidence_block) if evidence_block else "No specific local guideline chunks matched."

        if workflow_state == "CLINICAL_INTAKE_REQUIRED" and intake_questions:
            questions_str = "\n".join([f"- {q}" for q in intake_questions])
            task_instruction = (
                "TASK: The patient's symptom description is currently incomplete under the SOCRATES clinical history framework. "
                "Acknowledge their symptoms empathetically, explain briefly why a few clarifying details are needed, "
                f"and naturally ask these specific clarifying questions:\n{questions_str}"
            )
        else:
            diff_str = ""
            if differentials:
                diff_str = "\nIdentified ICD-11 Differential Considerations:\n" + "\n".join(
                    [f"- {d['condition_name']} (ICD-11: {d['icd11_code']}, Confidence: {d['confidence']})" for d in differentials]
                )
            task_instruction = (
                "TASK: Synthesize a structured, natural clinical decision support assessment grounded strictly in the "
                "retrieved evidence chunks above. Include:\n"
                "1. Empathetic interpretation of the patient's complex/colloquial symptom narrative.\n"
                "2. Evidence-grounded clinical considerations with inline [Ref 1], [Ref 2] citations.\n"
                "3. Recommended diagnostic workup / laboratory investigations to discuss with their physician.\n"
                "4. Mandatory Clinical Safety Netting & red-flag escalation instructions."
                f"{diff_str}"
            )

        return (
            f"Patient Demographics: Age Cohort={age_group}, Biological Sex={biological_sex}\n"
            f"PHI-Scrubbed Patient Narrative: \"{redacted_query}\"\n"
            f"Normalized Clinical Interpretation: \"{normalized_query}\"\n\n"
            f"VERIFIED INSTITUTIONAL CLINICAL EVIDENCE:\n{evidence_str}\n\n"
            f"{task_instruction}\n\n"
            f"LANGUAGE DIRECTIVE: {lang_instruction}"
        )

    def verify_llm_output_safety(self, llm_text: str, fallback_text: str) -> Tuple[str, bool]:
        """
        Verifies that the Cloud LLM output adheres to clinical non-prescribing guardrails.
        If any unsafe pattern is detected, reverts immediately to the deterministic fallback.
        """
        if not llm_text or len(llm_text.strip()) < 20:
            return fallback_text, False

        lower = llm_text.lower()
        for forbidden in self.FORBIDDEN_UNSAFE_PATTERNS:
            if forbidden in lower:
                logger.warning("Cloud LLM output triggered safety guardrail ('%s'). Reverting to deterministic output.", forbidden)
                return fallback_text, False

        return llm_text.strip(), True

    async def _call_gemini_async(self, prompt: str, history: List[Dict[str, str]]) -> Optional[str]:
        api_key = self._get_api_key("gemini")
        model = self._get_model("gemini")
        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        contents = []
        for turn in history:
            role = "user" if turn.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "systemInstruction": {"parts": [{"text": self.CLINICAL_SYSTEM_PROMPT}]},
            "contents": contents,
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "maxOutputTokens": settings.LLM_MAX_TOKENS
            }
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, params={"key": api_key}, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return "".join(p.get("text", "") for p in parts)
            else:
                logger.warning("Gemini API returned status %d: %s", resp.status_code, resp.text[:200])
        return None

    async def _call_anthropic_async(self, prompt: str, history: List[Dict[str, str]]) -> Optional[str]:
        api_key = self._get_api_key("anthropic")
        model = self._get_model("anthropic")
        if not api_key:
            return None

        url = "https://api.anthropic.com/v1/messages"
        messages = []
        for turn in history:
            role = "user" if turn.get("role") == "user" else "assistant"
            if turn.get("content"):
                messages.append({"role": role, "content": turn["content"]})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "temperature": settings.LLM_TEMPERATURE,
            "system": self.CLINICAL_SYSTEM_PROMPT,
            "messages": messages
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content_blocks = data.get("content", [])
                if content_blocks:
                    return "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
            else:
                logger.warning("Anthropic Claude API returned status %d: %s", resp.status_code, resp.text[:200])
        return None

    async def _call_openai_async(self, prompt: str, history: List[Dict[str, str]]) -> Optional[str]:
        api_key = self._get_api_key("openai")
        model = self._get_model("openai")
        if not api_key:
            return None

        url = "https://api.openai.com/v1/chat/completions"
        messages = [{"role": "system", "content": self.CLINICAL_SYSTEM_PROMPT}]
        for turn in history:
            role = "user" if turn.get("role") == "user" else "assistant"
            if turn.get("content"):
                messages.append({"role": role, "content": turn["content"]})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content")
            else:
                logger.warning("OpenAI API returned status %d: %s", resp.status_code, resp.text[:200])
        return None

    async def synthesize_hybrid_response_async(
        self,
        raw_patient_query: str,
        context_chunks: List[Dict[str, Any]],
        deterministic_fallback_text: str,
        language: str = "en",
        workflow_state: str = "STRUCTURED_ASSESSMENT",
        intake_questions: Optional[List[str]] = None,
        differentials: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        age_group: str = "ADULT",
        biological_sex: str = "UNSPECIFIED"
    ) -> Dict[str, Any]:
        """
        Executes the full Hybrid Cloud LLM synthesis pipeline asynchronously:
        1. Scrubs PHI from patient query and conversation history
        2. Normalizes complex/colloquial/Singlish narratives
        3. Calls active Cloud LLM (Gemini 1.5 Pro / Claude 3.5 Sonnet / GPT-4o) if configured
        4. Verifies post-inference clinical safety guardrails
        5. Falls back gracefully to `deterministic_fallback_text` if offline or local mode
        """
        nlu_data = self.normalize_complex_patient_narrative(raw_patient_query)
        scrubbed_history, history_entities = self.scrub_conversation_history(conversation_history)
        all_scrubbed = sorted(list(set(nlu_data["scrubbed_entities"] + history_entities)))

        provider, model_name = self.resolve_active_provider()
        if provider == "local":
            return {
                "response_text": deterministic_fallback_text,
                "provider_used": "local_deterministic",
                "model_used": model_name,
                "cloud_synthesized": False,
                "redacted_query": nlu_data["redacted_text"],
                "normalized_query": nlu_data["normalized_clinical_query"],
                "scrubbed_entities": all_scrubbed
            }

        prompt = self._build_grounded_prompt(
            redacted_query=nlu_data["redacted_text"],
            normalized_query=nlu_data["normalized_clinical_query"],
            context_chunks=context_chunks,
            language=language,
            workflow_state=workflow_state,
            intake_questions=intake_questions,
            differentials=differentials,
            age_group=age_group,
            biological_sex=biological_sex
        )

        cloud_output: Optional[str] = None
        try:
            if provider == "gemini":
                cloud_output = await self._call_gemini_async(prompt, scrubbed_history)
            elif provider == "anthropic":
                cloud_output = await self._call_anthropic_async(prompt, scrubbed_history)
            elif provider == "openai":
                cloud_output = await self._call_openai_async(prompt, scrubbed_history)
        except Exception as e:
            logger.warning("Hybrid Cloud LLM (%s) request failed, falling back to local deterministic engine: %s", provider, str(e))
            cloud_output = None

        if cloud_output:
            verified_text, passed_safety = self.verify_llm_output_safety(cloud_output, deterministic_fallback_text)
            if passed_safety:
                return {
                    "response_text": verified_text,
                    "provider_used": provider,
                    "model_used": model_name,
                    "cloud_synthesized": True,
                    "redacted_query": nlu_data["redacted_text"],
                    "normalized_query": nlu_data["normalized_clinical_query"],
                    "scrubbed_entities": all_scrubbed
                }

        return {
            "response_text": deterministic_fallback_text,
            "provider_used": "local_deterministic_fallback",
            "model_used": "MedGuard-Local-Deterministic-RAG",
            "cloud_synthesized": False,
            "redacted_query": nlu_data["redacted_text"],
            "normalized_query": nlu_data["normalized_clinical_query"],
            "scrubbed_entities": all_scrubbed
        }


hybrid_llm_connector = HybridLLMConnector()

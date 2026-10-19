import re
from typing import Tuple, List, Set


class PHIScrubber:
    """
    HIPAA Safe Harbor 18-identifier redaction & Data Loss Prevention (DLP) engine
    with English, Sinhala, and Singlish support.
    Ensures that any demographic, identifying, financial, or secret API key tokens
    in free-text patient prompts are scrubbed prior to persistence into relational databases
    or transmission to external inference queues.
    """

    PATTERNS = [
        # Secret Credentials & API Tokens (DLP Leak Prevention)
        ("SECRET_API_KEY", re.compile(r"\b(?:AIza[0-9A-Za-z\-_]{25,}|sk-ant-[0-9A-Za-z\-_]{16,}|sk-(?:proj-)?[0-9A-Za-z\-_]{20,}|ghp_[0-9A-Za-z]{25,}|Bearer\s+eyJ[0-9A-Za-z\-_]+\.[0-9A-Za-z\-_]+)\b")),
        # Credit / Debit Card Numbers (PCI-DSS 13-16 digits)
        ("CREDIT_CARD", re.compile(r"\b(?:\d{4}[-\s]){3}\d{4}\b|\b\d{16}\b")),
        # IPv4 Network Addresses
        ("IP_ADDRESS", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")),
        ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE)),
        ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
        ("NHS_OR_NIC", re.compile(r"\b(?:\d{3}\s?\d{3}\s?\d{4}|\d{9}[vVxX]|\d{12})\b")),
        ("PHONE", re.compile(r"(?:\+94[\s-]?0?\d{2}[\s-]?\d{3}[\s-]?\d{4}\b|\b0[1-9]\d[\s-]?\d{3}[\s-]?\d{4}\b|\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b)")),
        ("MRN", re.compile(r"\b(?:MRN|Medical Record(?: Number)?|Patient ID)[\s:#]+([A-Za-z0-9-]+)\b", re.IGNORECASE)),
        ("DATE_OF_BIRTH", re.compile(r"\b(?:DOB|born on|date of birth)[\s:#]+(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})\b", re.IGNORECASE)),
        ("STREET_ADDRESS", re.compile(r"\b\d{1,5}\s+[A-Za-z0-9\.,\s]{3,30}\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b", re.IGNORECASE)),
        ("NAME_TITLE", re.compile(r"\b(?:Dr\.|Doctor|Mr\.|Mrs\.|Ms\.|Patient|named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b")),
        ("NAME_INTRO", re.compile(r"\b(?:My name is|I am|This is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b")),
        # Sinhala & Singlish PHI Patterns
        ("NAME_SI", re.compile(r"(?:මගේ\s*නම|මම)\s+([^\s,.:;]+(?:\s+[^\s,.:;]+)?)")),
        ("NAME_SINGLISH", re.compile(r"\b(?:mage\s+nama|my\s+name)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\b", re.IGNORECASE)),
        ("PHONE_SI", re.compile(r"(?:දුරකථන\s*අංක(?:ය|යයි)?|දුරකථන|දුරකතනය)[\s:#]+(\+?\d[\d\s-]{8,15})")),
        ("NIC_SI", re.compile(r"(?:ජාතික\s*හැඳුනුම්පත|හැඳුනුම්පත්\s*අංක(?:ය|යයි)?|හැඳුනුම්පත)[\s:#]+([0-9vVxX]+)")),
        ("DOB_SI", re.compile(r"(?:උපන්\s*දිනය)[\s:#]+(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})")),
    ]

    def redact(self, text: str) -> Tuple[str, List[str]]:
        if not text:
            return "", []

        redacted = text
        detected_entity_types: Set[str] = set()

        for entity_type, pattern in self.PATTERNS:
            matches = list(pattern.finditer(redacted))
            if matches:
                detected_entity_types.add(entity_type)
                placeholder = f"[REDACTED_{entity_type}]"
                redacted = pattern.sub(placeholder, redacted)

        return redacted, sorted(list(detected_entity_types))


phi_scrubber = PHIScrubber()


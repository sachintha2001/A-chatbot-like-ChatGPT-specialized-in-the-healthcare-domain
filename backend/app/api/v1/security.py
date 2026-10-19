from fastapi import APIRouter
from app.compliance.security_shield import security_shield
from app.compliance.phi_scrubber import phi_scrubber

router = APIRouter(
    prefix="/security",
    tags=["Zero-Trust Security Shield, Anti-Malware & DLP Compliance"],
)


@router.get("/status")
async def get_security_shield_status():
    """
    Returns live Zero-Trust Security Shield posture, anti-malware file inspection telemetry,
    active WAF defenses, and Zero-Leakage Data Loss Prevention (DLP) rules.
    """
    posture = security_shield.get_security_posture()
    posture["phi_scrubber_categories"] = [p[0] for p in phi_scrubber.PATTERNS]
    return posture


@router.post("/self-test")
async def execute_security_self_diagnostic():
    """
    Executes a live, non-destructive 6-Point Anti-Malware, Anti-Virus, WAF & Zero-Leakage DLP
    Self-Diagnostic Verification Suite:
    1. EICAR Standard Antivirus Test Signature Blocker
    2. Disguised Windows PE/Executable Magic-Byte Blocker
    3. Malicious PDF Active JavaScript / Launch Exploit Blocker
    4. Adversarial Prompt Injection & Secret Exfiltration WAF
    5. SQL Injection & Cross-Site Scripting (XSS) WAF
    6. Zero-Leakage PHI & Cloud API Key Outbound DLP Scrubber
    """
    return security_shield.run_self_diagnostic_suite()

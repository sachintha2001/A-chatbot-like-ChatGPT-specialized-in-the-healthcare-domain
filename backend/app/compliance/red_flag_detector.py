import re
from typing import List, Dict, Any, Tuple, Optional
from app.config import settings


class DeterministicRedFlagDetector:
    """
    Pre-inference clinical triage safety barrier with bilingual (English + Sinhala) capabilities.
    Evaluates patient narratives deterministically against high-acuity clinical protocols
    (ACS, Stroke FAST, Sepsis, Severe Dyspnea, Anaphylaxis, Neuroglycopenia, and Suicidality)
    prior to any language model invocation, ensuring sub-millisecond escalation for life threats.
    """

    RED_FLAG_PROTOCOLS: Dict[str, Dict[str, Any]] = {
        "ACUTE_CORONARY_SYNDROME": {
            "patterns": [
                r"\b(crushing|heavy|squeezing|tightness|pressure)\b.*?\b(chest|breastbone|sternum)\b",
                r"\b(chest pain|chest pressure)\b.*?\b(radiat(ing|es)|jaw|neck|left arm|shoulder|back)\b",
                r"\b(chest pain|chest pressure)\b.*?\b(sweat(ing)?|diaphoresis|cold sweat|clammy|nausea)\b",
                r"\b(heart attack|myocardial infarction|infarct)\b",
                # Sinhala clinical patterns
                r"(පපුව(ේ)?\s*(තද\s*)?(කැක්කුම|වේදනාව|හිරවීම|බර ගතිය|මිරිකීම))",
                r"(වම්\s*අතට|බෙල්ලට|හනුවට|පිටුපසට)\s*(විහිදෙන|පැතිරෙන|යන)\s*(පපුවේ\s*)?(වේදනාව|කැක්කුම)",
                r"(හෘදයාබාධ(ය|යක්)?|හාට්\s*ඇටෑක්)",
                r"(පපුවේ\s*වේදනාව\s*සමඟ\s*(දහඩිය|හුස්ම\s*ගැනීමේ\s*අපහසුව))",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "Immediate activation of Emergency Medical Services. Do not drive to hospital. Rest in a seated position while awaiting paramedics.",
            "clinical_directive_si": "වහාම හදිසි ගිලන්රථ සේවාව අමතන්න (ශ්‍රී ලංකාව: 1990 සුවසැරිය). රෝහල වෙත තනිවම රිය ධාවනය නොකරන්න. ගිලන්රථය පැමිණෙන තුරු සන්සුන්ව වාඩි වී සිටින්න.",
            "category": "Cardiovascular"
        },
        "ACUTE_ISCHEMIC_STROKE": {
            "patterns": [
                r"\b(droop(ing)?|sagging)\b.*?\b(face|mouth|eyelid|smile)\b",
                r"\b(weakness|numb(ness)?|can'?t move|paraly(zed|sis))\b.*?\b(one side|arm|leg|face|unilateral)\b",
                r"\b(slurr(ed|ing)|cannot speak|difficulty speaking|garbled words|aphasia|lost speech)\b",
                r"\b(sudden loss of vision|double vision|sudden blindness)\b",
                r"\b(sudden loss of balance|unable to stand|severe sudden vertigo)\b",
                r"\b(thunderclap headache|worst headache of life)\b",
                # Sinhala clinical patterns
                r"(මුහුණ\s*(පැත්තකට\s*)?(ඇදවීම|එල්ලාවැටීම|අක්‍රිය වීම))",
                r"(අත|කකුල|එක්\s*පැත්තක්)\s*(පණ\s*නැතිවීම|හිරිවැටීම|චලනය\s*කළ\s*නොහැකි)",
                r"(කතා\s*(කරගැනීමට|කරන්න)\s*(අපහසු|නොහැකි|බැරි)|වචන\s*පැටලීම|කතාව\s*නැතිවීම)",
                r"(අංශභාග(ය|යක්)?|ස්ට්‍රෝක්|හදිසි\s*දරුණු\s*හිසරදය)",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "Suspected Acute Stroke (FAST criteria positive). Note time of symptom onset immediately. Thrombolysis / thrombectomy eligibility depends on rapid transit to a designated Primary Stroke Center.",
            "clinical_directive_si": "හදිසි අංශභාග තත්ත්වයක් (Acute Stroke - FAST නිර්ණායක ධනාත්මකයි). රෝග ලක්ෂණ ආරම්භ වූ වේලාව සටහන් කරගෙන වහාම ළඟම ඇති ප්‍රධාන රෝහලක හදිසි ප්‍රතිකාර ඒකකයට (ETU) රෝගියා යොමු කරන්න.",
            "category": "Neurological"
        },
        "SEVERE_RESPIRATORY_DISTRESS": {
            "patterns": [
                r"\b(cannot breathe|can'?t breathe|gasping for air|suffocating)\b",
                r"\b(blue lips|blue face|cyanosis|turning blue)\b",
                r"\b(stridor|harsh high-pitched breathing|airway clos(ing|ed))\b",
                r"\b(severe asthma attack)\b.*?\b(inhaler not working|no relief)\b",
                r"\b(cough(ing)? up blood|hemoptysis)\b.*?\b(pleuritic|chest pain|swollen calf)\b",
                # Sinhala clinical patterns
                r"(හුස්ම\s*(ගැනීමට|ගන්න)\s*(අපහසු|නොහැකි|බැරි)|හුස්ම\s*හිරවීම|හුස්ම\s*මදිවීම)",
                r"(තොල්\s*(නිල්\s*වීම|කළු\s*වීම)|මුහුණ\s*නිල්\s*වීම)",
                r"(දරුණු\s*ඇදුම\s*(අමාරුව|තත්ත්වය)|ඉන්හේලර්\s*(වැඩ\s*නොකරයි|සහනයක්\s*නැත))",
                r"(ලේ\s*කැස්ස|හුස්ම\s*ගන්නා\s*විට\s*දැඩි\s*ශබ්දය)",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "Severe Acute Respiratory Distress with impending respiratory fatigue. Maintain upright posture. Dispatch emergency paramedics for immediate supplemental high-flow oxygen.",
            "clinical_directive_si": "දරුණු ශ්වසන අපහසුතාවයක් සහ හුස්ම ගැනීමේ විඩාව. රෝගියා කෙළින් වාඩි කරවා තබන්න. ක්ෂණික ඔක්සිජන් ප්‍රතිකාරය සඳහා වහාම හදිසි ගිලන්රථ සේවාව අමතන්න.",
            "category": "Pulmonary"
        },
        "ANAPHYLAXIS": {
            "patterns": [
                r"\b(throat clos(ing|ed)|tongue swell(ing|ed)|lip swell(ing|ed)|angioedema)\b",
                r"\b(swollen (throat|tongue|lips))\b.*?\b(breathing difficulty|rash|hives|wheez(e|ing))\b",
                r"\b(allergic reaction)\b.*?\b(epipen|epinephrine|cannot swallow|passing out)\b",
                r"\b(peanut|bee sting|nut allergy)\b.*?\b(throat|dizzy|collapse|swollen)\b",
                # Sinhala clinical patterns
                r"(උගුර\s*ඉදිමීම|දිව\s*ඉදිමීම|තොල්\s*ඉදිමීම)",
                r"(බඹර|දෙබර|මී\s*මැසි)\s*(දෂ්ට|විදීම|ඇනීම)",
                r"(දරුණු\s*ආසාත්මිකතා(ව|වයක්)?|ඇනෆිලැක්සිස්)",
                r"(කෑමක්|ඖෂධයක්\s*ගැනීමෙන්\s*පසු\s*(හුස්ම\s*හිරවීම|පලු\s*දැමීම))",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "Suspected Severe Anaphylaxis. Administer Intramuscular Epinephrine Auto-Injector (EpiPen 0.3mg/0.5mg) into anterolateral mid-thigh immediately. Keep patient supine with legs elevated. Call 911/999.",
            "clinical_directive_si": "දරුණු ජීවිත අනතුරුදායක ආසාත්මිකතාවයක් (Anaphylaxis). එපිනෙෆ්‍රින් (EpiPen) තිබේ නම් වහාම කලවයේ පිටත පෙදෙසට ලබාදෙන්න. රෝගියා වැතිර පාද ඉහළට ඔසවා තබන්න. වහාම 1990 අමතන්න.",
            "category": "Immunological"
        },
        "SEPTIC_SHOCK": {
            "patterns": [
                r"\b(high fever|shivering|rigors)\b.*?\b(confus(ed|ion)|unresponsive|lethargic|delirious)\b",
                r"\b(infection|wound|fever)\b.*?\b(no urine|haven'?t peed|anuria|extremely low blood pressure)\b",
                r"\b(non-blanching rash|purple spots|petechiae|purpura)\b",
                r"\b(mottled skin|cold extremities|septic|sepsis)\b",
                # Sinhala clinical patterns
                r"(අධික\s*උණ|දැඩි\s*වෙව්ලීම|ගැහීම)\s*සමඟ\s*(සිහිමද|සිහිය\s*නැති|විකාරයෙන්)",
                r"(සෙප්සිස්|ලේ\s*විෂ\s*වීම|මුත්රා\s*පිට\s*නොවීම)",
                r"(සමෙහි\s*දම්\s*පැහැ\s*ලප|සම\s*අයිස්\s*සේ\s*සීතල\s*වීම)",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "High Clinical Probability of Sepsis / Impending Septic Shock (qSOFA trigger). Requires immediate emergency resuscitation, IV antibiotics, and serum lactate clearance within the 1-hour window.",
            "clinical_directive_si": "සෙප්සිස් (Sepsis / රුධිර විෂ වීම) හෝ සෙප්ටික් කම්පනය පිළිබඳ බරපතල අවදානමක්. පැය 1ක් ඇතුළත රෝහල්ගත කර හදිසි ප්‍රතිජීවක සහ IV සේලයින් ලබාදිය යුතුය.",
            "category": "Infectious Disease"
        },
        "NEUROGLYCOPENIC_COMA": {
            "patterns": [
                r"\b(diabetic)\b.*?\b(unconscious|passed out|seizure|convulsion|cannot wake up)\b",
                r"\b(blood sugar|glucose)\b.*?\b(below 40|below 35|below 30|extremely low|critically low)\b",
                r"\b(severe hypoglycemia)\b.*?\b(confus(ed|ion)|aggressive|seizing|coma)\b",
                # Sinhala clinical patterns
                r"(දියවැඩියා(ව)?\s*රෝගියා\s*(සිහිනැතිව|වෙව්ලමින්|අපස්මාරය))",
                r"(රුධිර\s*සීනි\s*මට්ටම\s*(40ට\s*අඩු|30ට\s*අඩු|අධික\s*ලෙස\s*අඩුවීම))",
                r"(දරුණු\s*හයිපොග්ලයිසීමියාව|සීනි\s*බැසීම\s*නිසා\s*සිහිමුර්ඡා\s*වීම)",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "Severe Level 3 Neuroglycopenia. Do not give oral fluids or food due to aspiration risk. Administer nasal or intramuscular glucagon immediately and summon emergency rescue.",
            "clinical_directive_si": "දරුණු සීනි අඩුවීමක් (Hypoglycemic Coma). සිහිය නොමැති බැවින් කටින් දියර හෝ ආහාර ලබා නොදෙන්න (පෙනහළුවලට යාමේ අවදානම). වහාම හදිසි ගිලන්රථ සේවාව අමතන්න.",
            "category": "Endocrine"
        },
        "SUICIDAL_CRISIS": {
            "patterns": [
                r"\b(want to kill myself|commit suicide|end my life|going to kill myself)\b",
                r"\b(swallowed (a whole bottle|all my pills)|overdosed on)\b",
                r"\b(plan to hang myself|cut my wrists|shoot myself)\b",
                # Sinhala clinical patterns
                r"(දිවි\s*නසාගැනීමට|ජීවිතය\s*නැතිකරගැනීමට|මැරෙන්න\s*ඕන(ෙ)?)",
                r"(බෙහෙත්\s*පෙති\s*ඔක්කොම\s*බිව්වා|වස\s*බිව්වා|අධිමාත්‍රාවක්\s*ගත්තා)",
            ],
            "severity": "EMERGENCY",
            "clinical_directive": "Active self-harm or suicidal crisis identified. Connect immediately with Crisis & Suicide Lifeline or attend the nearest Emergency Department. You are not alone.",
            "clinical_directive_si": "ක්ෂණික මානසික සුව සහන සේවාව අමතන්න (ශ්‍රී ලංකාව: 1926 ජාතික මානසික සෞඛ්‍ය උපකාරක සේවාව / 1333). ඔබ තනිවී නැත, කරුණාකර වහාම සහය පතන්න.",
            "category": "Psychiatric Emergency"
        }
    }

    def __init__(self):
        # Precompile regular expressions for microsecond execution overhead
        self.compiled_rules = {
            syndrome: [re.compile(pat, re.IGNORECASE) for pat in cfg["patterns"]]
            for syndrome, cfg in self.RED_FLAG_PROTOCOLS.items()
        }

    def is_sinhala(self, text: str) -> bool:
        """Determines if text contains Sinhala Unicode codepoints."""
        return bool(re.search(r"[\u0D80-\u0DFF]", text))

    def evaluate(
        self,
        patient_narrative: str,
        preferred_language: Optional[str] = None
    ) -> Tuple[bool, List[str], str, Dict[str, str]]:
        matched_syndromes: List[str] = []
        directive: str = ""

        narrative_clean = patient_narrative.strip()
        is_si = preferred_language == "si" or self.is_sinhala(narrative_clean)

        for syndrome, patterns in self.compiled_rules.items():
            for regex in patterns:
                if regex.search(narrative_clean):
                    matched_syndromes.append(syndrome)
                    # Take highest acuity directive matching requested language
                    if not directive:
                        cfg = self.RED_FLAG_PROTOCOLS[syndrome]
                        directive = cfg.get("clinical_directive_si" if is_si else "clinical_directive", cfg["clinical_directive"])
                    break

        is_emergency = len(matched_syndromes) > 0

        hotline_numbers = {
            "Sri_Lanka_Suwa_Seriya": settings.EMERGENCY_ESCALATION_HOTLINE_LK,
            "Sri_Lanka_Mental_Health": settings.SUICIDE_CRISIS_LIFELINE_LK,
            "UK_Emergency": settings.EMERGENCY_ESCALATION_HOTLINE_UK,
            "US_Canada_Emergency": settings.EMERGENCY_ESCALATION_HOTLINE_US,
            "EU_Emergency": settings.EMERGENCY_ESCALATION_HOTLINE_EU,
            "Suicide_Crisis_Lifeline": settings.SUICIDE_CRISIS_LIFELINE,
        }

        return is_emergency, matched_syndromes, directive, hotline_numbers


red_flag_detector = DeterministicRedFlagDetector()

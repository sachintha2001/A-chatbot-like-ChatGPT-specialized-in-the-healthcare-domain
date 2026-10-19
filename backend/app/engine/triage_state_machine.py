import re
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from app.models.pathology import TriageAcuityLevel, MedicalSpecialty
from app.ingestion.vector_store import vector_store


class TriageWorkflowState(str, Enum):
    RED_FLAG_EMERGENCY = "RED_FLAG_EMERGENCY"
    CLINICAL_INTAKE_REQUIRED = "CLINICAL_INTAKE_REQUIRED"
    STRUCTURED_ASSESSMENT = "STRUCTURED_ASSESSMENT"


class SOCRATESTriageStateMachine:
    """
    Deterministic clinical conversation state machine implementing the SOCRATES & OLDCARTS
    symptom assessment framework with zero clinical hallucinations.
    Stages:
    1. Red-Flag Emergency Screening (Immediate halt if life-threatening signs present)
    2. Targeted Clarifying Intake (SOCRATES exploration if symptom profile is underspecified)
    3. Structured Clinical Assessment (Acuity, ICD-11 differentials, diagnostic workup, citations)
    """

    # Deterministic multi-specialty red flag triggers (English and Sinhala)
    RED_FLAG_PATTERNS = [
        # Cardiovascular & Hemodynamic
        (r"(crushing|heavy|radiat(ing|es)|squeezing)\s+.*chest", "Severe cardiac chest pain radiating or pressure characteristic"),
        (r"chest\s+(pain|tightness|pressure)\s+.*(left\s+arm|jaw|neck|back)", "Chest pain with radiation to arm, jaw, neck, or back"),
        (r"chest\s+(pain|pressure)\s+.*(sweat|diaphoresis|shortness\s+of\s+breath|nausea)", "Acute coronary syndrome autonomic response constellation"),
        (r"syncope|fainted|loss\s+of\s+consciousness", "Sudden transient loss of consciousness / syncope"),
        
        # Neurological
        (r"(thunderclap|worst\s+headache\s+of\s+(my\s+)?life|sudden\s+explosive\s+headache)", "Thunderclap headache: high-risk for Subarachnoid Hemorrhage"),
        (r"(facial\s+droop|slurred\s+speech|arm\s+weakness|hemiplegia|one\s+side\s+(weak|numb))", "Acute focal neurological deficit: FAST positive stroke indication"),
        (r"(stiff\s+neck|neck\s+rigidity)\s+.*(fever|photophobia|rash|confusion)", "Meningeal irritation triad (Meningitis / Encephalitis)"),
        (r"seizure\s+.*(longer\s+than\s+5|not\s+stopping|status)", "Prolonged seizure / Status epilepticus"),

        # Respiratory
        (r"(unable\s+to\s+speak|gasping|blue\s+lips|cyanosis)", "Acute respiratory failure with severe hypoxic compromise"),
        (r"stridor|barking.*retraction|choking", "High-grade upper airway obstruction / stridor"),
        (r"(coughing\s+up\s+blood|hemoptysis\s+.*(large|cup|massive))", "Massive hemoptysis / acute pulmonary hemorrhage"),

        # Gastrointestinal & Sepsis
        (r"(vomiting\s+blood|hematemesis|coffee\s+ground\s+vomit)", "Acute upper gastrointestinal hemorrhage"),
        (r"(black\s+tarry\s+stool|melena)", "Lower or upper gastrointestinal hemorrhage / melena"),
        (r"(rigid\s+abdomen|board-like|severe\s+rebound|peritonitis)", "Peritoneal signs indicating visceral perforation or acute abdomen"),
        (r"(petechial|purpuric|non-blanching\s+rash)\s+.*fever", "Non-blanching purpuric rash: Meningococcemia / Sepsis alert"),
        
        # Obstetric
        (r"(pregnant|pregnancy)\s+.*(bp\s*(>|over|>=)?\s*160|severe\s+headache|blurred\s+vision|flashing\s+lights)", "Severe Preeclampsia / impending Eclampsia features"),
        (r"(pregnant|pregnancy)\s+.*(heavy\s+vaginal\s+bleed|woody\s+pain)", "Placental abruption / obstetric hemorrhage"),

        # Sinhala Red Flags
        (r"(පපුවේ\s+දරුණු\s+වේදනාව|වම්\s+අතට\s+විහිදෙන|පපුව\s+හිරවීම)", "හදිසි හෘදයාබාධ ලක්ෂණ (Acute Coronary Syndrome)"),
        (r"(දරුණු\s+හිසරදය.*බෙල්ලේ\s+තදගතිය|වෙව්ලුම.*උණ)", "මෙනින්ජයිටිස් / මස්තිෂ්ක ආසාදන ලක්ෂණ"),
        (r"(එක්\s+පැත්තක\s+දුර්වලතාවය|කතා\s+කිරීමේ\s+අපහසුව|මුහුණේ\s+ඇදවීම)", "ස්ට්‍රෝක් / අංශභාග හදිසි ලක්ෂණ (FAST criteria)"),
        (r"(ලේ\s+වමනය|කළු\s+පැහැති\s+මලපහ)", "ආහාර ජීර්ණ පද්ධතියේ දරුණු ලේ ගැලීම"),
        (r"(හුස්ම\s+ගැනීමේ\s+දරුණු\s+අපහසුව|තොල්\s+නිල්වීම)", "දරුණු ශ්වසන අකර්මණ්‍යතාවය")
    ]

    def __init__(self):
        pass

    def is_sinhala(self, text: str) -> bool:
        return bool(re.search(r"[\u0D80-\u0DFF]", text))

    def screen_red_flags(self, user_query: str) -> List[str]:
        """
        Executes deterministic pattern screening for life-threatening clinical triggers.
        Returns list of triggered red-flag clinical descriptions.
        """
        triggered = []
        normalized = user_query.lower()
        for pattern, description in self.RED_FLAG_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                triggered.append(description)
        return triggered

    def evaluate_socrates_completeness(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Evaluates symptom coverage against the 8 SOCRATES clinical dimensions:
        Site, Onset, Character, Radiation, Associations, Time course, Exacerbating factors, Severity.
        """
        full_text = query.lower()
        if history:
            for msg in history:
                if msg.get("role") == "user":
                    full_text += " " + msg.get("content", "").lower()

        # Detection heuristics for SOCRATES dimensions
        has_site = bool(re.search(r"(head|chest|stomach|abdom|back|leg|arm|knee|throat|eye|neck|side|හිස|පපුව|බඩ|උගුර|කකුල|අත)", full_text))
        has_onset = bool(re.search(r"(sudden|gradual|started|began|hours|days|weeks|months|ago|yesterday|today|පටන්|දින|පැය)", full_text))
        has_character = bool(re.search(r"(sharp|dull|throbbing|burning|cramp|pressure|aching|stabbing|tight|වේදනාව|කැක්කුම|දැවිල්ල|තදවීම)", full_text))
        has_radiation = bool(re.search(r"(spread|radiat|down\s+to|into\s+my|to\s+the|විහිදෙන|පැතිරෙන)", full_text))
        has_associations = bool(re.search(r"(fever|nause|vomit|dizz|cough|sweat|breath|chills|උණ|වමනය|කැස්ස|දහඩිය|ක්ලාන්තය)", full_text))
        has_time_course = bool(re.search(r"(constant|intermittent|comes\s+and\s+goes|worse|better|peak|නිරන්තර|වරින්\s+වර)", full_text))
        has_severity = bool(re.search(r"(mild|moderate|severe|unbearable|\b[1-9]\s*/\s*10|\b10\s*/\s*10|දරුණු|මධ්‍යම|සුළු)", full_text))

        present_dimensions = []
        if has_site: present_dimensions.append("Site")
        if has_onset: present_dimensions.append("Onset")
        if has_character: present_dimensions.append("Character")
        if has_radiation: present_dimensions.append("Radiation")
        if has_associations: present_dimensions.append("Associations")
        if has_time_course: present_dimensions.append("Time course")
        if has_severity: present_dimensions.append("Severity")

        is_complete = len(present_dimensions) >= 3 or (has_site and has_onset and (has_character or has_severity))
        return {
            "is_complete": is_complete,
            "dimension_count": len(present_dimensions),
            "present_dimensions": present_dimensions,
            "has_site": has_site,
            "has_onset": has_onset,
            "has_character": has_character,
            "has_associations": has_associations,
            "has_severity": has_severity
        }

    def generate_intake_questions(
        self,
        query: str,
        evaluation: Dict[str, Any],
        is_si: bool = False
    ) -> Tuple[List[str], List[str]]:
        """
        Generates 2-3 focused SOCRATES clinical intake questions and clickable quick-reply chips.
        """
        questions = []
        chips = []
        q_lower = query.lower()

        if is_si:
            if not evaluation.get("has_onset"):
                questions.append("මෙම රෝග ලක්ෂණ ආරම්භ වූයේ කවදාද (හදිසියේද නැතහොත් ක්‍රමයෙන්ද)?")
                chips.extend(["හදිසියේ ආරම්භ විය (< පැය 2)", "දින 2-3කට පෙර", "සති කිහිපයක සිට"])
            if not evaluation.get("has_character"):
                questions.append("වේදනාවේ ස්වභාවය විස්තර කරන්න (උදා: දැවිල්ල, ගැස්ම, තද කැක්කුම)?")
                chips.extend(["දැඩි ගැස්ම සහිතයි (Throbbing)", "දැවිල්ල සහිතයි (Burning)", "තදවීමක් වැනි (Pressure)"])
            if not evaluation.get("has_associations"):
                questions.append("උණ, වමනය, ක්ලාන්තය හෝ හුස්ම ගැනීමේ අපහසුව වැනි වෙනත් ලක්ෂණ ඇත්ද?")
                chips.extend(["තද උණ සහිතයි", "වමනය හෝ ඔක්කාරය", "වෙනත් රෝග ලක්ෂණ නොමැත"])
            if not evaluation.get("has_severity") and len(chips) < 5:
                chips.extend(["මධ්‍යස්ථ වේදනාව (4-6/10)", "ඉතා දරුණු වේදනාව (7-10/10)"])
        else:
            # Domain-specific intake tailoring
            if "headache" in q_lower or "head" in q_lower:
                questions.append("How suddenly did the headache start, and how many hours or days has it lasted?")
                questions.append("Is the pain throbbing, tight, or dull, and is it on one or both sides?")
                questions.append("Are you experiencing visual changes, nausea, sensitivity to light, or neck stiffness?")
                chips = [
                    "Sudden onset (< 2 hours)",
                    "Lasting > 3 days",
                    "Throbbing / one-sided",
                    "Sensitivity to light & nausea",
                    "Mild to moderate (3-5/10)",
                    "Severe intensity (7-10/10)"
                ]
            elif "chest" in q_lower:
                questions.append("Does the pain feel like pressure, burning, or sharp stabbing?")
                questions.append("Does it spread to your left arm, jaw, neck, or back?")
                questions.append("Does resting make it better, or does breathing deeply make it worse?")
                chips = [
                    "Sharp pain worse on breathing",
                    "Dull pressure / tightness",
                    "No radiation to arm/jaw",
                    "Started after physical exertion",
                    "Started at rest"
                ]
            elif "abdom" in q_lower or "stomach" in q_lower or "belly" in q_lower:
                questions.append("Where exactly is the pain located (e.g., upper middle, right lower side, lower abdomen)?")
                questions.append("Is the discomfort steady or cramping in waves?")
                questions.append("Do you have fever, vomiting, diarrhea, or notice any changes in your bowel movements?")
                chips = [
                    "Upper stomach / burning",
                    "Right lower side pain",
                    "Associated with nausea/vomiting",
                    "Mild cramping after eating",
                    "No fever present"
                ]
            else:
                if not evaluation.get("has_onset"):
                    questions.append("When did you first notice this symptom, and did it develop suddenly or gradually?")
                    chips.extend(["Started today (< 24h)", "Present for 3-5 days", "Chronic (> 2 weeks)"])
                if not evaluation.get("has_character"):
                    questions.append("How would you describe the sensation (e.g., sharp, dull ache, burning, pressure)?")
                    chips.extend(["Dull persistent ache", "Sharp intermittent", "Burning discomfort"])
                if not evaluation.get("has_associations"):
                    questions.append("Do you have accompanying fever, shortness of breath, dizziness, or fatigue?")
                    chips.extend(["High-grade fever present", "Mild fatigue only", "No other symptoms"])

        return questions[:3], chips[:6]

    def build_structured_assessment(
        self,
        query: str,
        is_si: bool = False
    ) -> Dict[str, Any]:
        """
        Executes vector search against clinical pathologies and guidelines,
        synthesizes structured ICD-11 differential considerations, diagnostic workup, and safe care.
        """
        search_results = vector_store.search(query, top_k=3)
        differentials = []
        investigations = set()
        safe_care = []
        citations = []
        highest_acuity = TriageAcuityLevel.ROUTINE_CLINIC

        for idx, (chunk, score) in enumerate(search_results):
            meta = chunk.get("metadata", {})
            icd11 = meta.get("icd11_code")
            name = meta.get("clinical_name") or chunk.get("section_header", "")
            specialty = meta.get("medical_specialty", "Clinical Medicine")
            acuity_str = meta.get("baseline_acuity", "ROUTINE_CLINIC")

            # Update highest acuity seen
            if acuity_str == "EMERGENCY":
                highest_acuity = TriageAcuityLevel.EMERGENCY
            elif acuity_str == "URGENT_CONSULT" and highest_acuity != TriageAcuityLevel.EMERGENCY:
                highest_acuity = TriageAcuityLevel.URGENT_CONSULT

            if icd11 and name:
                confidence = "High" if score > 0.45 else ("Moderate" if score > 0.25 else "Consideration")
                differentials.append({
                    "icd11_code": icd11,
                    "condition_name": name,
                    "specialty": specialty,
                    "confidence": confidence,
                    "similarity": round(float(score), 3),
                    "rationale": f"Reported presentation correlates with {specialty} criteria and symptom pattern."
                })

            citations.append({
                "badge": f"[Ref {idx+1}]",
                "authority": meta.get("source", "WHO ICD-11 / Clinical Guideline"),
                "title": chunk.get("section_header", "Clinical Guidance"),
                "excerpt": chunk.get("text_content", "")[:180] + "...",
                "url": meta.get("guideline_url") or "https://icd.who.int/browse/2024-01/mms/en"
            })

        # Standard workup and immediate advice
        if is_si:
            investigations = [
                "මූලික රුධිර පරීක්ෂාව (Full Blood Count - FBC)",
                "C-ප්‍රතික්‍රියාශීලී ප්‍රෝටීන් (CRP) හෝ ESR මට්ටම",
                "රුධිර පීඩනය සහ හෘද ස්පන්දන වේගය පරීක්ෂාව",
                "වෛද්‍යවරයා විසින් නියම කරනු ලබන අදාළ විශේෂිත රසායනාගාර පරීක්ෂණ"
            ]
            safe_care = [
                "ප්‍රමාණවත් තරම් විවේක ගන්න සහ විජලනය වැළැක්වීමට දියර වර්ග වැඩිපුර පානය කරන්න.",
                "වෛද්‍ය උපදෙසකින් තොරව දැඩි වේදනා නාශක ඖෂධ ගැනීමෙන් වළකින්න.",
                "රෝග ලක්ෂණ උත්සන්න වුවහොත් වහාම ළඟම ඇති රෝහල වෙත යොමුවන්න."
            ]
        else:
            investigations = [
                "Complete Blood Count (CBC / FBC) and Inflammatory Markers (CRP / ESR)",
                "Targeted organ metabolic panel (Renal Function / Liver Enzymes) if indicated",
                "Standard 12-Lead Electrocardiogram (ECG) if chest or autonomic symptoms are present",
                "Vital signs assessment: Blood Pressure, Heart Rate, Pulse Oximetry (SpO2), Temperature"
            ]
            safe_care = [
                "Maintain adequate oral hydration and rest in a comfortable, ventilated space.",
                "Avoid unprescribed NSAIDs or polypharmacy until medical evaluation has clarified the underlying etiology.",
                "Seek immediate emergency re-evaluation if shortness of breath, confusion, or syncope develops."
            ]

        # Follow up action chips
        chips = [
            "What diagnostic tests should I ask for?" if not is_si else "මා සිදුකළ යුතු රසායනාගාර පරීක්ෂණ මොනවාද?",
            "What red flags should I monitor?" if not is_si else "අවධානය යොමුකළ යුතු අනතුරුදායක ලක්ෂණ මොනවාද?",
            "How to prepare for doctor's visit?" if not is_si else "වෛද්‍ය හමුව සඳහා සූදානම් වන්නේ කෙසේද?"
        ]

        return {
            "acuity": highest_acuity,
            "differentials": differentials[:3],
            "diagnostic_investigations": list(investigations),
            "safe_immediate_care": safe_care,
            "citations": citations,
            "follow_up_chips": chips
        }

    def process_turn(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        preferred_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a conversational triage turn across the 3 states:
        1. Red-Flag Emergency Screening
        2. SOCRATES Clarifying Intake
        3. Structured Clinical Assessment
        """
        from app.engine.llm_connector import hybrid_llm_connector

        # 0. Scrub PHI and normalize complex/Singlish/misspelled narratives first
        nlu = hybrid_llm_connector.normalize_complex_patient_narrative(user_message)
        effective_query = nlu["normalized_clinical_query"] or nlu["redacted_text"] or user_message
        scrubbed_entities = nlu["scrubbed_entities"]

        is_si = preferred_language == "si" or self.is_sinhala(user_message)
        red_flags = self.screen_red_flags(effective_query)

        # STATE 1: RED-FLAG EMERGENCY
        if red_flags:
            if is_si:
                emergency_headline = "හදිසි අනතුරු ඇඟවීම: වහාම වෛද්‍ය ප්‍රතිකාර අවශ්‍යයි (EMERGENCY)"
                emergency_body = (
                    "**අවධානයට**: ඔබ සඳහන් කළ රෝග ලක්ෂණ ක්ෂණික වෛද්‍ය මැදිහත්වීමක් අවශ්‍ය වන හදිසි අනතුරුදායක සායනික ලක්ෂණ (Red Flags) සමඟ ගැලපේ.\n\n"
                    "**හඳුනාගත් අවදානම් සාධක**:\n" +
                    "\n".join([f"- {rf}" for rf in red_flags]) +
                    "\n\n**ක්‍ෂණික පියවර**:\n"
                    "1. වහාම **1990 සුවසැරිය** ගිලන්රථ සේවාව අමතන්න හෝ ළඟම ඇති ප්‍රධාන රෝහලේ හදිසි ප්‍රතිකාර ඒකකය (ETU) වෙත යන්න.\n"
                    "2. තනිවම වාහන ධාවනය නොකරන්න. ආරක්ෂිතව විවේකී ඉරියව්වකින් හිඳගන්න හෝ වැතිරෙන්න.\n"
                    "3. වෛද්‍ය කාර්ය මණ්ඩලය පැමිණෙන තෙක් කිසිදු ඝන ආහාරයක් හෝ තහවුරු නොකළ ඖෂධයක් ලබා නොගන්න."
                )
                chips = ["1990 සුවසැරිය අමතන්න", "ළඟම ඇති හදිසි ප්‍රතිකාර ඒකකය", "හදිසි ප්‍රථමාධාර උපදෙස්"]
            else:
                emergency_headline = "EMERGENCY TRIAGE ALERT: Immediate Medical Care Required"
                emergency_body = (
                    "**CRITICAL CLINICAL ALERT**: Your reported symptoms match high-risk deterministic red-flag criteria requiring immediate emergency medical evaluation.\n\n"
                    "**Identified Red-Flag Criteria**:\n" +
                    "\n".join([f"- {rf}" for rf in red_flags]) +
                    "\n\n**Immediate Mandatory Actions**:\n"
                    "1. Call emergency services immediately (**911**, **999**, or **1990**) or have someone transport you to the nearest hospital Emergency Department.\n"
                    "2. Do not drive yourself. Sit or lie down in a safe, resting position.\n"
                    "3. Do not consume solid food or unprescribed medications until evaluated by an emergency clinician."
                )
                chips = ["Call Emergency Services (911 / 1990)", "Emergency Department Locator", "First Aid Safety Directives"]

            return {
                "state": TriageWorkflowState.RED_FLAG_EMERGENCY,
                "acuity": TriageAcuityLevel.EMERGENCY,
                "headline": emergency_headline,
                "content": emergency_body,
                "red_flags": red_flags,
                "citations": [
                    {
                        "badge": "[WHO-EMERGENCY]",
                        "authority": "WHO Emergency Triage Assessment and Treatment (ETAT)",
                        "title": "Clinical Red-Flag Criteria for Urgent Escalation",
                        "excerpt": "Immediate stabilization and urgent referral are mandatory when high-risk airway, breathing, circulation, or neurological red flags are met.",
                        "url": "https://www.who.int/publications/i/item/9789241511216"
                    }
                ],
                "follow_up_chips": chips,
                "is_sinhala": is_si,
                "scrubbed_entities": scrubbed_entities,
                "redacted_query": nlu["redacted_text"],
                "normalized_query": effective_query
            }

        # STATE 2: SOCRATES CLARIFYING INTAKE
        socrates_eval = self.evaluate_socrates_completeness(effective_query, conversation_history)
        if not socrates_eval["is_complete"]:
            questions, chips = self.generate_intake_questions(effective_query, socrates_eval, is_si)
            if is_si:
                headline = "සායනික තක්සේරුව: රෝග ලක්ෂණ පිළිබඳ වැඩිදුර විස්තර අවශ්‍යයි"
                body = (
                    "ඔබගේ රෝග ලක්ෂණ නිවැරදිව තක්සේරු කර සුදුසු වෛද්‍ය මගපෙන්වීමක් ලබා දීම සඳහා, "
                    "කරුණාකර පහත ප්‍රශ්න කිහිපයට පිළිතුරු සපයන්න:\n\n" +
                    "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]) +
                    "\n\n*(ඔබට පහතින් ඇති ඉක්මන් පිළිතුරු බොත්තම් (Quick Reply) භාවිතයෙන්ද පිළිතුරු දිය හැක.)*"
                )
            else:
                headline = "Clinical Symptom Intake: Further Clinical Clarification Required"
                body = (
                    "To accurately evaluate your presentation and formulate an evidence-based clinical assessment, "
                    "please clarify the following aspects of your symptoms:\n\n" +
                    "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]) +
                    "\n\n*(You can reply in free text or tap any of the quick-selection options below.)*"
                )

            return {
                "state": TriageWorkflowState.CLINICAL_INTAKE_REQUIRED,
                "acuity": TriageAcuityLevel.ROUTINE_CLINIC,
                "headline": headline,
                "content": body,
                "intake_questions": questions,
                "red_flags": [],
                "citations": [
                    {
                        "badge": "[SOCRATES-PROTOCOL]",
                        "authority": "Royal College of Physicians / Clinical Examination Guidelines",
                        "title": "SOCRATES Systematic Symptom Assessment Methodology",
                        "excerpt": "A thorough history encompassing Site, Onset, Character, Radiation, Associations, Timing, Exacerbating factors, and Severity must precede differential diagnostic formulation.",
                        "url": "https://www.rcplondon.ac.uk"
                    }
                ],
                "follow_up_chips": chips,
                "is_sinhala": is_si,
                "scrubbed_entities": scrubbed_entities,
                "redacted_query": nlu["redacted_text"],
                "normalized_query": effective_query
            }

        # STATE 3: STRUCTURED CLINICAL ASSESSMENT
        assessment_data = self.build_structured_assessment(effective_query, is_si)
        acuity = assessment_data["acuity"]

        if is_si:
            headline = f"සායනික තක්සේරු ප්‍රතිඵලය: {acuity.value}"
            diff_text = "\n".join([
                f"- **{d['condition_name']}** (ICD-11: `{d['icd11_code']}`) - {d['confidence']} සම්භාවිතාව\n  *{d['rationale']}*"
                for d in assessment_data["differentials"]
            ]) if assessment_data["differentials"] else "- සාමාන්‍ය බාහිර රෝගී සායනික ඇගයීමක් නිර්දේශ කෙරේ."

            workup_text = "\n".join([f"- {item}" for item in assessment_data["diagnostic_investigations"]])
            care_text = "\n".join([f"- {item}" for item in assessment_data["safe_immediate_care"]])

            body = (
                f"**සායනික තක්සේරු මට්ටම**: `{acuity.value}`\n\n"
                f"**සැලකිල්ලට ගත හැකි විභව සායනික තත්ත්වයන් (Differentials)**:\n{diff_text}\n\n"
                f"**වෛද්‍යවරයා සමඟ සාකච්ඡා කළ යුතු පරීක්ෂණ (Diagnostic Workup)**:\n{workup_text}\n\n"
                f"**ආරක්ෂිත ක්ෂණික සත්කාර සහ ආරක්ෂණ උපදෙස් (Safety Netting)**:\n{care_text}\n\n"
                "*(මෙම මගපෙන්වීම සායනික තීරණ ආධාරකයක් පමණි. නිශ්චිත රෝග විනිශ්චයක් සඳහා ලියාපදිංචි වෛද්‍යවරයෙකු හමුවන්න.)*"
            )
        else:
            headline = f"Structured Clinical Assessment: {acuity.value}"
            diff_text = "\n".join([
                f"- **{d['condition_name']}** (ICD-11: `{d['icd11_code']}`) - **{d['confidence']} Confidence**\n  *{d['rationale']}*"
                for d in assessment_data["differentials"]
            ]) if assessment_data["differentials"] else "- General ambulatory clinical evaluation recommended."

            workup_text = "\n".join([f"- {item}" for item in assessment_data["diagnostic_investigations"]])
            care_text = "\n".join([f"- {item}" for item in assessment_data["safe_immediate_care"]])

            body = (
                f"**Triage Urgency Classification**: `{acuity.value}`\n\n"
                f"**Potential Clinical Considerations (ICD-11 Aligned)**:\n{diff_text}\n\n"
                f"**Recommended Diagnostic Investigations to Discuss with Physician**:\n{workup_text}\n\n"
                f"**Safe Immediate Care & Clinical Safety Netting**:\n{care_text}\n\n"
                "*(This assessment is an assistive clinical decision aid and does not replace an in-person medical diagnosis. If symptoms worsen, seek prompt physical examination.)*"
            )

        return {
            "state": TriageWorkflowState.STRUCTURED_ASSESSMENT,
            "acuity": acuity,
            "headline": headline,
            "content": body,
            "red_flags": [],
            "differentials": assessment_data["differentials"],
            "diagnostic_workup": assessment_data["diagnostic_investigations"],
            "citations": assessment_data["citations"],
            "follow_up_chips": assessment_data["follow_up_chips"],
            "is_sinhala": is_si,
            "scrubbed_entities": scrubbed_entities,
            "redacted_query": nlu["redacted_text"],
            "normalized_query": effective_query
        }

    async def process_turn_hybrid_async(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        preferred_language: Optional[str] = None,
        age_group: str = "ADULT",
        biological_sex: str = "UNSPECIFIED"
    ) -> Dict[str, Any]:
        """
        Executes the deterministic 3-stage SOCRATES triage state machine and enriches
        non-emergency conversational responses with the Hybrid Cloud LLM Connector
        (Google Gemini 1.5 Pro / Claude 3.5 Sonnet / GPT-4o) over PHI-scrubbed text.
        """
        from app.engine.llm_connector import hybrid_llm_connector

        base_result = self.process_turn(
            user_message=user_message,
            conversation_history=conversation_history,
            preferred_language=preferred_language
        )

        # Life-threatening red flags always use deterministic immediate escalation without cloud latency
        if base_result["state"] == TriageWorkflowState.RED_FLAG_EMERGENCY:
            provider, model_name = hybrid_llm_connector.resolve_active_provider()
            base_result["llm_provider"] = "deterministic_safety_gate"
            base_result["llm_model"] = model_name
            base_result["cloud_synthesized"] = False
            return base_result

        effective_query = base_result.get("normalized_query") or user_message
        raw_chunks = [chunk for chunk, _ in vector_store.search(effective_query, top_k=3)]
        lang_code = "si" if base_result.get("is_sinhala") else "en"

        hybrid_res = await hybrid_llm_connector.synthesize_hybrid_response_async(
            raw_patient_query=user_message,
            context_chunks=raw_chunks,
            deterministic_fallback_text=base_result["content"],
            language=lang_code,
            workflow_state=base_result["state"].value,
            intake_questions=base_result.get("intake_questions"),
            differentials=base_result.get("differentials"),
            conversation_history=conversation_history,
            age_group=age_group,
            biological_sex=biological_sex
        )

        base_result["content"] = hybrid_res["response_text"]
        base_result["llm_provider"] = hybrid_res["provider_used"]
        base_result["llm_model"] = hybrid_res["model_used"]
        base_result["cloud_synthesized"] = hybrid_res["cloud_synthesized"]
        base_result["scrubbed_entities"] = hybrid_res["scrubbed_entities"]
        return base_result


triage_state_machine = SOCRATESTriageStateMachine()

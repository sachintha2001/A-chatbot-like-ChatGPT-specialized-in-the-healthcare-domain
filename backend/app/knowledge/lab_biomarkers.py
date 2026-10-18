"""
Clinical Laboratory Biomarker Knowledge Registry.
Contains authoritative clinical reference intervals, critical panic limits,
and physiological interpretations based on WHO, IFCC, NHS, and ADLM (AACC) standards.
Provides dual-language (English + Sinhala) clinical terminology.
"""

from typing import Dict, Any, Optional, List


CLINICAL_BIOMARKER_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ----------------------------------------------------
    # 1. FULL BLOOD COUNT (FBC / CBC)
    # ----------------------------------------------------
    "hemoglobin": {
        "canonical_id": "hemoglobin",
        "aliases": ["hb", "hgb", "hemoglobin", "haemoglobin", "හිමොග්ලොබින්"],
        "display_name_en": "Hemoglobin (Hb)",
        "display_name_si": "හිමොග්ලොබින් මට්ටම (Hemoglobin)",
        "category": "Full Blood Count (FBC / CBC)",
        "unit": "g/dL",
        "ref_min": 12.0,
        "ref_max": 17.5,
        "panic_low": 7.0,
        "panic_high": 20.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated hemoglobin indicates hemoconcentration (severe dehydration, plasma leakage in dengue), polycythemia vera, or chronic hypoxic lung disease.",
        "elevated_interpretation_si": "හිමොග්ලොබින් මට්ටම ඉහළ යාමෙන් දරුණු විජලනය, ඩෙංගු රෝගයේදී ප්ලාස්මා කාන්දු වීම (Hemoconcentration), හෝ පොලිසයිතීමියා තත්ත්වය පෙන්නුම් කරයි.",
        "decreased_interpretation_en": "Decreased hemoglobin indicates anemia (iron deficiency, chronic disease, hemolysis, or acute blood loss). Critical levels (< 7.0 g/dL) may require blood transfusion.",
        "decreased_interpretation_si": "හිමොග්ලොබින් මට්ටම පහළ යාම රක්තහීනතාවය (Anemia) හෝ අභ්‍යන්තර ලේ ගැලීමක් පෙන්නුම් කරයි. 7.0 g/dL ට වඩා අඩු වීම හදිසි රුධිර පාරවිලයනයක් අවශ්‍ය විය හැකි තත්ත්වයකි.",
        "related_icd11": ["3A00", "CA22", "1D2Z"]
    },
    "platelets": {
        "canonical_id": "platelets",
        "aliases": ["platelet", "platelets", "plt", "platelet count", "plateletcount", "thrombocytes", "පට්ටිකා", "පට්ටිකා ප්‍රමාණය"],
        "display_name_en": "Platelet Count (PLT)",
        "display_name_si": "රුධිර පට්ටිකා ප්‍රමාණය (Platelet Count)",
        "category": "Full Blood Count (FBC / CBC)",
        "unit": "/uL",
        "ref_min": 150000,
        "ref_max": 450000,
        "panic_low": 50000,
        "panic_high": 1000000,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated platelets (Thrombocytosis) occurs in reactive inflammatory states, acute infection, iron deficiency, or essential thrombocythemia.",
        "elevated_interpretation_si": "පට්ටිකා ප්‍රමාණය ඉහළ යාම (Thrombocytosis) උග්‍ර ආසාදන, ශරීරයේ දැවිල්ල හෝ රුධිර සෛල අක්‍රමිකතා හේතුවෙන් සිදුවිය හැක.",
        "decreased_interpretation_en": "Decreased platelets (Thrombocytopenia) is a hallmark of Dengue hemorrhagic fever (critical phase leakage), immune thrombocytopenia (ITP), drug-induced bone marrow suppression, or severe sepsis.",
        "decreased_interpretation_si": "පට්ටිකා ප්‍රමාණය අඩුවීම (Thrombocytopenia) ඩෙංගු උණ රෝගයේ අවදානම් අවධිය (Critical phase), ප්‍රතිශක්තිකරණ රෝග (ITP), හෝ සෙප්සිස් ආසාදන තත්ත්වයන්හි ප්‍රධාන ලක්ෂණයකි. 50,000 ට වඩා අඩු වීම හදිසි රෝහල්ගත වීමක් අවශ්‍ය ලක්ෂණයකි.",
        "related_icd11": ["1D2Z", "3A00", "1C12"]
    },
    "wbc": {
        "canonical_id": "wbc",
        "aliases": ["wbc", "white blood cells", "total wbc", "leukocytes", "සුදු රුධිරාණු"],
        "display_name_en": "Total White Blood Cells (WBC)",
        "display_name_si": "මුළු සුදු රුධිරාණු ප්‍රමාණය (Total WBC)",
        "category": "Full Blood Count (FBC / CBC)",
        "unit": "/uL",
        "ref_min": 4000,
        "ref_max": 11000,
        "panic_low": 2000,
        "panic_high": 30000,
        "is_qualitative": False,
        "elevated_interpretation_en": "Leukocytosis indicates acute bacterial infection, severe systemic inflammation, tissue necrosis, or hematologic malignancy.",
        "elevated_interpretation_si": "සුදු රුධිරාණු ප්‍රමාණය වැඩි වීමෙන් උග්‍ර බැක්ටීරියා ආසාදනයක්, පටක ප්‍රදාහයක් (Inflammation) හෝ සෙප්සිස් තත්ත්වයක් පෙන්නුම් කරයි.",
        "decreased_interpretation_en": "Leukopenia indicates acute viral suppression (Dengue early phase, viral hepatitis), severe neutropenic sepsis, or autoimmune bone marrow suppression.",
        "decreased_interpretation_si": "සුදු රුධිරාණු ප්‍රමාණය අඩුවීම ඩෙංගු වැනි වෛරස් ආසාදනවල මුල් අවධියේදී හෝ ප්‍රතිශක්තිකරණ ඌනතා තත්ත්වයන්හිදී දැකිය හැක.",
        "related_icd11": ["1D2Z", "CA40", "1C12"]
    },
    "hematocrit": {
        "canonical_id": "hematocrit",
        "aliases": ["hematocrit", "haematocrit", "pcv", "packed cell volume", "හෙමටොක්‍රිට්"],
        "display_name_en": "Packed Cell Volume (PCV / Hematocrit)",
        "display_name_si": "රුධිර සෛල පරිමාව (PCV / Hematocrit)",
        "category": "Full Blood Count (FBC / CBC)",
        "unit": "%",
        "ref_min": 36.0,
        "ref_max": 52.0,
        "panic_low": 20.0,
        "panic_high": 58.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated PCV (Hemoconcentration) is a critical objective monitoring marker for vascular plasma leakage in Dengue fever, or severe dehydration.",
        "elevated_interpretation_si": "PCV අගය ඉහළ යාම (Hemoconcentration) ඩෙංගු රෝගයේදී රුධිර වාහිනී තුළින් ප්ලාස්මා කාන්දු වීමේ ප්‍රධාන දර්ශකයකි. මෙය හදිසි තරල ප්‍රතිකාර අවශ්‍ය බව අඟවයි.",
        "decreased_interpretation_en": "Decreased PCV indicates blood dilution (fluid overload), active internal hemorrhage, or severe anemia.",
        "decreased_interpretation_si": "PCV අගය පහළ යාම අධික ලෙස තරල ශරීරගත වීම හෝ රුධිර වහනයක් (Hemorrhage) සිදුවීම පෙන්නුම් කරයි.",
        "related_icd11": ["1D2Z", "3A00"]
    },

    # ----------------------------------------------------
    # 2. GLYCEMIC & METABOLIC PROFILE
    # ----------------------------------------------------
    "fasting_blood_sugar": {
        "canonical_id": "fasting_blood_sugar",
        "aliases": ["fbs", "fasting blood sugar", "fasting glucose", "fasting blood glucose", "නිරාහාර රුධිර සීනි"],
        "display_name_en": "Fasting Blood Sugar (FBS)",
        "display_name_si": "නිරාහාර රුධිර සීනි මට්ටම (FBS)",
        "category": "Glycemic Profile",
        "unit": "mg/dL",
        "ref_min": 70.0,
        "ref_max": 99.0,
        "panic_low": 54.0,
        "panic_high": 350.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "FBS 100-125 mg/dL indicates Impaired Fasting Glucose (Prediabetes); FBS >= 126 mg/dL confirms Diabetes Mellitus per WHO and ADA diagnostic criteria.",
        "elevated_interpretation_si": "FBS අගය 100-125 mg/dL අතර වීම පූර්ව දියවැඩියාව (Prediabetes) වන අතර 126 mg/dL හෝ ඊට වැඩි වීම දියවැඩියා රෝගය (Diabetes Mellitus) තහවුරු කරයි.",
        "decreased_interpretation_en": "Hypoglycemia (< 70 mg/dL, panic < 54 mg/dL). Immediate administration of 15-20g fast-acting oral glucose or IV Dextrose is required to prevent neuroglycopenic seizure.",
        "decreased_interpretation_si": "හයිපොග්ලයිසීමියාව (රුධිර සීනි 70 mg/dL ට අඩු වීම). ක්ෂණිකව සීනි හෝ ග්ලූකෝස් පානය කළ යුතුය. 54 mg/dL ට අඩු වීම සිහිසුන් වීමේ අවදානමක් සහිත හදිසි තත්ත්වයකි.",
        "related_icd11": ["5A11", "5A10"]
    },
    "hba1c": {
        "canonical_id": "hba1c",
        "aliases": ["hba1c", "glycated hemoglobin", "glycosylated hemoglobin", "a1c", "එච්බීඒවන්සී"],
        "display_name_en": "Glycated Hemoglobin (HbA1c)",
        "display_name_si": "ත්‍රෛමාසික සාමාන්‍ය රුධිර සීනි ප්‍රතිශතය (HbA1c)",
        "category": "Glycemic Profile",
        "unit": "%",
        "ref_min": 4.0,
        "ref_max": 5.6,
        "panic_low": 3.5,
        "panic_high": 12.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "HbA1c 5.7-6.4% indicates Prediabetes. HbA1c >= 6.5% confirms Type 2 Diabetes Mellitus. Values > 8.0% indicate suboptimal glycemic control with microvascular complication risk.",
        "elevated_interpretation_si": "HbA1c 5.7%-6.4% පූර්ව දියවැඩියාව ද, 6.5% ට වැඩි වීම දියවැඩියාව ද තහවුරු කරයි. 8.0% ට වැඩි වීම ඇස්, වකුගඩු සහ ස්නායු ආබාධ ඇතිවීමේ අවදානම ඉහළ නංවයි.",
        "decreased_interpretation_en": "Low HbA1c is commonly seen in shortened red cell survival (hemolytic anemia, frequent blood donation, severe hemoglobinopathy) or pregnancy.",
        "decreased_interpretation_si": "HbA1c අගය ඉතා අඩු වීම රක්තපාත රක්තහීනතාවය (Hemolytic anemia) හෝ ගර්භණීභාවයේදී දැකිය හැක.",
        "related_icd11": ["5A11", "5A10"]
    },

    # ----------------------------------------------------
    # 3. LIPID PROFILE
    # ----------------------------------------------------
    "total_cholesterol": {
        "canonical_id": "total_cholesterol",
        "aliases": ["total cholesterol", "cholesterol", "කොලෙස්ටරෝල්"],
        "display_name_en": "Total Cholesterol",
        "display_name_si": "මුළු කොලෙස්ටරෝල් මට්ටම (Total Cholesterol)",
        "category": "Lipid Profile",
        "unit": "mg/dL",
        "ref_min": 120.0,
        "ref_max": 200.0,
        "panic_low": 70.0,
        "panic_high": 400.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Total cholesterol >= 200 mg/dL indicates hypercholesterolemia. Values >= 240 mg/dL double the relative risk of atherosclerotic coronary artery disease.",
        "elevated_interpretation_si": "කොලෙස්ටරෝල් 200 mg/dL ට වැඩි වීම හෘද රෝග සහ රුධිර නාල අවහිර වීමේ අවදානම වැඩි කරයි. ආහාර පාලනය සහ ප්‍රතිකාර අවශ්‍ය වේ.",
        "decreased_interpretation_en": "Hypocholesterolemia (< 120 mg/dL) can be observed in severe hyperthyroidism, severe malnutrition, or advanced hepatic cirrhosis.",
        "decreased_interpretation_si": "අධික ලෙස කොලෙස්ටරෝල් අඩු වීම අක්මාවේ දරුණු දුර්වලතා හෝ තයිරොයිඩ් අධික්‍රියාකාරීත්වය නිසා සිදුවිය හැක.",
        "related_icd11": ["5C80", "BA80"]
    },
    "ldl_cholesterol": {
        "canonical_id": "ldl_cholesterol",
        "aliases": ["ldl", "ldl cholesterol", "bad cholesterol", "අහිතකර කොලෙස්ටරෝල්"],
        "display_name_en": "LDL Cholesterol (Low-Density Lipoprotein)",
        "display_name_si": "අහිතකර කොලෙස්ටරෝල් (LDL Cholesterol)",
        "category": "Lipid Profile",
        "unit": "mg/dL",
        "ref_min": 50.0,
        "ref_max": 100.0,
        "panic_low": 30.0,
        "panic_high": 300.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated LDL ('bad cholesterol') >= 100 mg/dL (and especially >= 160 mg/dL) accelerates atheromatous plaque formation in coronary and carotid arteries.",
        "elevated_interpretation_si": "LDL හෙවත් අහිතකර කොලෙස්ටරෝල් 100 mg/dL ට වඩා වැඩි වීම හෘදයාබාධ (Heart attack) සහ අංශභාග (Stroke) ඇතිවීමේ ප්‍රධාන අවදානම් සාධකයකි.",
        "decreased_interpretation_en": "Target LDL < 70 mg/dL (or < 55 mg/dL) is standard clinical practice in established cardiovascular disease.",
        "decreased_interpretation_si": "හෘද රෝගීන් සඳහා LDL අගය 70 mg/dL ට වඩා අඩුවෙන් පවත්වා ගැනීම නිර්දේශිත සායනික ඉලක්කයකි.",
        "related_icd11": ["5C80", "BA80", "8B11"]
    },
    "hdl_cholesterol": {
        "canonical_id": "hdl_cholesterol",
        "aliases": ["hdl", "hdl cholesterol", "good cholesterol", "හිතකර කොලෙස්ටරෝල්"],
        "display_name_en": "HDL Cholesterol (High-Density Lipoprotein)",
        "display_name_si": "හිතකර කොලෙස්ටරෝල් (HDL Cholesterol)",
        "category": "Lipid Profile",
        "unit": "mg/dL",
        "ref_min": 40.0,
        "ref_max": 80.0,
        "panic_low": 20.0,
        "panic_high": 120.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated HDL (> 60 mg/dL) is cardioprotective, facilitating reverse cholesterol transport away from arterial walls back to the liver.",
        "elevated_interpretation_si": "HDL 60 mg/dL ට වඩා ඉහළ මට්ටමක පැවතීම හදවතට ආරක්ෂාකාරී වේ (Cardioprotective).",
        "decreased_interpretation_en": "Low HDL (< 40 mg/dL in men, < 50 mg/dL in women) is an independent cardiovascular risk factor associated with metabolic syndrome and insulin resistance.",
        "decreased_interpretation_si": "HDL 40 mg/dL ට වඩා අඩු වීම හෘද රෝග ඇතිවීමේ අවදානම ඉහළ නංවයි. දිනපතා ව්‍යායාම සහ සෞඛ්‍ය සම්පන්න ආහාර මඟින් මෙය වැඩි කරගත හැක.",
        "related_icd11": ["5C80", "BA80"]
    },
    "triglycerides": {
        "canonical_id": "triglycerides",
        "aliases": ["triglycerides", "tg", "ට්‍රයිග්ලිසරයිඩ්"],
        "display_name_en": "Serum Triglycerides (TG)",
        "display_name_si": "ට්‍රයිග්ලිසරයිඩ් මේද මට්ටම (Triglycerides)",
        "category": "Lipid Profile",
        "unit": "mg/dL",
        "ref_min": 50.0,
        "ref_max": 150.0,
        "panic_low": 30.0,
        "panic_high": 500.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated triglycerides (>= 150 mg/dL). Severe hypertriglyceridemia (>= 500 mg/dL) carries an acute risk of life-threatening Acute Pancreatitis.",
        "elevated_interpretation_si": "ට්‍රයිග්ලිසරයිඩ් මට්ටම 150 mg/dL ට වඩා වැඩි වීම හෘද රෝග අවදානම වැඩි කරයි. 500 mg/dL ට වැඩි වීම අග්න්‍යාශයේ ප්‍රදාහය (Acute Pancreatitis) ඇතිකළ හැකි හදිසි තත්ත්වයකි.",
        "decreased_interpretation_en": "Low triglycerides (< 50 mg/dL) are seen in malabsorption, severe malnutrition, or extreme dietary fat restriction.",
        "decreased_interpretation_si": "ට්‍රයිග්ලිසරයිඩ් අගය ඉතා අඩු වීම මන්දපෝෂණය හෝ මේදය අවශෝෂණය නොවීම නිසා සිදුවිය හැක.",
        "related_icd11": ["5C80", "DC31"]
    },

    # ----------------------------------------------------
    # 4. RENAL FUNCTION PROFILE (RFT / KFT)
    # ----------------------------------------------------
    "serum_creatinine": {
        "canonical_id": "serum_creatinine",
        "aliases": ["creatinine", "serum creatinine", "creat", "ක්‍රියැටිනින්"],
        "display_name_en": "Serum Creatinine",
        "display_name_si": "සීරම් ක්‍රියැටිනින් මට්ටම (Serum Creatinine)",
        "category": "Renal Function Profile (RFT / KFT)",
        "unit": "mg/dL",
        "ref_min": 0.6,
        "ref_max": 1.2,
        "panic_low": 0.3,
        "panic_high": 3.5,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated creatinine indicates impaired renal filtration: Acute Kidney Injury (AKI) or Chronic Kidney Disease (CKD). Panic levels (> 3.0 mg/dL) require urgent nephrological intervention.",
        "elevated_interpretation_si": "ක්‍රියැටිනින් මට්ටම වැඩිවීම වකුගඩුවල පෙරීමේ හැකියාව දුර්වල වී ඇති බව අඟවයි (වකුගඩු අකර්මණ්‍යතාවය - AKI හෝ CKD). 3.0 mg/dL ට වැඩි වීම හදිසි වෛද්‍ය ප්‍රතිකාර අවශ්‍ය තත්ත්වයකි.",
        "decreased_interpretation_en": "Low creatinine reflects low muscle mass (sarcopenia, advanced age) or pregnancy (increased GFR).",
        "decreased_interpretation_si": "ක්‍රියැටිනින් අගය අඩු වීම මාංශ පේශි ස්කන්ධය අඩු වීම හෝ ගර්භණී සමයේදී සාමාන්‍ය ලෙස දැකිය හැක.",
        "related_icd11": ["GB61", "GB60"]
    },
    "egfr": {
        "canonical_id": "egfr",
        "aliases": ["egfr", "gfr", "estimated gfr", "glomerular filtration rate", "ඊජීඑෆ්ආර්"],
        "display_name_en": "Estimated GFR (eGFR)",
        "display_name_si": "වකුගඩු පෙරීමේ අනුපාතය (eGFR)",
        "category": "Renal Function Profile (RFT / KFT)",
        "unit": "mL/min/1.73m2",
        "ref_min": 90.0,
        "ref_max": 130.0,
        "panic_low": 15.0,
        "panic_high": 160.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Hyperfiltration may occur in early diabetic nephropathy or pregnancy.",
        "elevated_interpretation_si": "eGFR අගය අධික ලෙස ඉහළ යාම දියවැඩියාවේ මුල් අවධියේදී දැකිය හැක.",
        "decreased_interpretation_en": "eGFR < 60 indicates Chronic Kidney Disease (Stage G3). eGFR < 15 indicates End-Stage Kidney Failure (Stage G5) requiring renal replacement therapy (dialysis or transplant).",
        "decreased_interpretation_si": "eGFR අගය 60 ට වඩා අඩුවීම නිදන්ගත වකුගඩු රෝගය (CKD) පෙන්නුම් කරයි. 15 ට වඩා අඩු වීම වකුගඩු සම්පූර්ණයෙන්ම අකර්මණ්‍ය වීමක් වන අතර ඩයලයිසිස් ප්‍රතිකාර අවශ්‍ය වේ.",
        "related_icd11": ["GB61", "GB60"]
    },
    "potassium": {
        "canonical_id": "potassium",
        "aliases": ["potassium", "serum potassium", "k+", "පොටෑසියම්"],
        "display_name_en": "Serum Potassium (K+)",
        "display_name_si": "සීරම් පොටෑසියම් මට්ටම (Potassium)",
        "category": "Renal Function Profile (RFT / KFT)",
        "unit": "mmol/L",
        "ref_min": 3.5,
        "ref_max": 5.0,
        "panic_low": 2.8,
        "panic_high": 6.2,
        "is_qualitative": False,
        "elevated_interpretation_en": "Hyperkalemia (> 5.0 mmol/L, panic > 6.0 mmol/L) is a critical cardiac emergency causing peaked T waves, conduction block, and fatal ventricular arrhythmias.",
        "elevated_interpretation_si": "පොටෑසියම් මට්ටම ඉහළ යාම (Hyperkalemia) හෘද ස්පන්දනය නතර වීමේ අවදානමක් ඇති කළ හැකි බරපතල හදිසි අවස්ථාවකි. වහාම රෝහල්ගත විය යුතුය.",
        "decreased_interpretation_en": "Hypokalemia (< 3.5 mmol/L, panic < 2.8 mmol/L) triggers muscle weakness, paralysis, constipation, and ventricular dysrhythmias.",
        "decreased_interpretation_si": "පොටෑසියම් අඩුවීම (Hypokalemia) මාංශ පේශි වේදනාව, අප්‍රාණිකත්වය සහ හෘද රිද්ම අක්‍රමිකතා ඇති කරයි.",
        "related_icd11": ["GB60", "BC81.3"]
    },

    # ----------------------------------------------------
    # 5. LIVER FUNCTION PROFILE (LFT)
    # ----------------------------------------------------
    "alt": {
        "canonical_id": "alt",
        "aliases": ["alt", "sgpt", "alanine transaminase", "alanine aminotransferase", "ඒඑල්ටී"],
        "display_name_en": "ALT (SGPT) - Alanine Aminotransferase",
        "display_name_si": "අක්මා එන්සයිම මට්ටම (ALT / SGPT)",
        "category": "Liver Function Profile (LFT)",
        "unit": "U/L",
        "ref_min": 7.0,
        "ref_max": 55.0,
        "panic_low": 2.0,
        "panic_high": 500.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated ALT is the most specific biomarker for hepatocellular injury: Viral Hepatitis, Non-Alcoholic Fatty Liver Disease (NAFLD), drug toxicity, or Dengue hepatic involvement.",
        "elevated_interpretation_si": "ALT අගය ඉහළ යාම අක්මාවේ සෛල විනාශ වීමක් හෝ ප්‍රදාහයක් (Hepatitis, Fatty Liver, ඩෙංගු අක්මා ආසාදන) පෙන්නුම් කරයි.",
        "decreased_interpretation_en": "Normal finding; very low levels lack clinical diagnostic significance.",
        "decreased_interpretation_si": "සාමාන්‍ය තත්ත්වයකි. සායනික ගැටලුවක් නොවේ.",
        "related_icd11": ["1E51", "DB93", "1D2Z"]
    },
    "ast": {
        "canonical_id": "ast",
        "aliases": ["ast", "sgot", "aspartate transaminase", "aspartate aminotransferase", "ඒඑස්ටී"],
        "display_name_en": "AST (SGOT) - Aspartate Aminotransferase",
        "display_name_si": "අක්මා එන්සයිම මට්ටම (AST / SGOT)",
        "category": "Liver Function Profile (LFT)",
        "unit": "U/L",
        "ref_min": 8.0,
        "ref_max": 48.0,
        "panic_low": 2.0,
        "panic_high": 500.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated AST is seen in acute liver injury, alcoholic liver disease (AST/ALT ratio > 2), myocardial necrosis, or acute skeletal muscle injury (rhabdomyolysis).",
        "elevated_interpretation_si": "AST අගය ඉහළ යාම අක්මාව, හෘදය හෝ මාංශ පේශිවලට සිදුවන හානි පෙන්නුම් කරයි.",
        "decreased_interpretation_en": "Normal finding; lacks clinical pathology significance.",
        "decreased_interpretation_si": "සාමාන්‍ය නිරෝගී තත්ත්වයකි.",
        "related_icd11": ["DB93", "1E51", "BA41"]
    },
    "bilirubin": {
        "canonical_id": "bilirubin",
        "aliases": ["bilirubin", "total bilirubin", "t.bili", "බිලිරුබින්"],
        "display_name_en": "Total Bilirubin",
        "display_name_si": "සීරම් බිලිරුබින් මට්ටම (Total Bilirubin)",
        "category": "Liver Function Profile (LFT)",
        "unit": "mg/dL",
        "ref_min": 0.2,
        "ref_max": 1.2,
        "panic_low": 0.0,
        "panic_high": 15.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated bilirubin (> 1.2 mg/dL; clinical jaundice visible at > 2.5 mg/dL) points to biliary obstruction, acute hepatitis, cirrhosis, or intravascular hemolysis.",
        "elevated_interpretation_si": "බිලිරුබින් අගය 1.2 mg/dL ට වඩා වැඩි වීම සෙංගමාලය (Jaundice), පිත නාල අවහිරතා හෝ රතු රුධිර සෛල විනාශ වීම පෙන්නුම් කරයි.",
        "decreased_interpretation_en": "Normal finding without pathological implication.",
        "decreased_interpretation_si": "සාමාන්‍ය නිරෝගී තත්ත්වයකි.",
        "related_icd11": ["DB93", "1E51"]
    },

    # ----------------------------------------------------
    # 6. INFECTIOUS & INFLAMMATORY SEROLOGY / CARDIAC
    # ----------------------------------------------------
    "dengue_ns1": {
        "canonical_id": "dengue_ns1",
        "aliases": ["dengue ns1", "ns1 antigen", "ns1", "dengue antigen", "ඩෙංගු එන්එස්1"],
        "display_name_en": "Dengue NS1 Antigen",
        "display_name_si": "ඩෙංගු NS1 ඇන්ටිජන් පරීක්ෂාව (Dengue NS1)",
        "category": "Infectious Disease Serology",
        "unit": "Qualitative",
        "ref_min": 0,
        "ref_max": 0,
        "is_qualitative": True,
        "positive_interpretation_en": "POSITIVE: Confirms acute active Dengue virus infection (Days 1-4 of fever). Patient requires daily Full Blood Count (FBC) monitoring for platelet drop and hematocrit rise, strict rest, and fluid management.",
        "positive_interpretation_si": "ධනාත්මකයි (POSITIVE): උග්‍ර ඩෙංගු වෛරස් ආසාදනය තහවුරු කරයි. වහාම වෛද්‍යවරයෙකු හමුවී දිනපතා රුධිර පරීක්ෂණ (FBC) සිදුකිරීම, විවේකය සහ නියමිත පරිදි දියර වර්ග පානය කිරීම අනිවාර්ය වේ. NSAIDs (Ibuprofen/Diclofenac) කිසිසේත් නොගත යුතුය.",
        "negative_interpretation_en": "NEGATIVE: No Dengue NS1 antigen detected. If fever persists > 5 days, secondary Dengue IgM/IgG antibodies or alternative febrile etiologies (Leptospirosis, Typhoid, Viral illness) should be investigated.",
        "negative_interpretation_si": "සෘණාත්මකයි (NEGATIVE): ඩෙංගු ඇන්ටිජන් හඳුනාගෙන නොමැත. උණ දින 3කට වඩා පවතී නම් නැවත රුධිර පරීක්ෂාවක් හෝ වෙනත් ආසාදන සඳහා පරීක්ෂා කළ යුතුය.",
        "related_icd11": ["1D2Z"]
    },
    "troponin": {
        "canonical_id": "troponin",
        "aliases": ["troponin", "troponin i", "troponin t", "hs-troponin", "trop i", "ට්‍රොපොනින්"],
        "display_name_en": "Cardiac Troponin (cTnI / cTnT)",
        "display_name_si": "හෘද ට්‍රොපොනින් පරීක්ෂාව (Cardiac Troponin)",
        "category": "Cardiac Biomarkers",
        "unit": "ng/mL",
        "ref_min": 0.0,
        "ref_max": 0.04,
        "panic_low": 0.0,
        "panic_high": 0.1,
        "is_qualitative": False,
        "elevated_interpretation_en": "ELEVATED / POSITIVE: Indicates acute myocardial necrosis (Acute Myocardial Infarction / Heart Attack). Immediate emergency department transfer, 12-lead ECG, antiplatelet therapy, and urgent cardiology assessment are mandatory.",
        "elevated_interpretation_si": "ඉහළ ගොස් ඇත (POSITIVE / ELEVATED): හෘද පේශි සෛල මියයාම (හෘදයාබාධයක් - Heart Attack) තහවුරු කරයි. වහාම ළඟම ඇති රෝහලේ හදිසි ප්‍රතිකාර ඒකකය (ETU) වෙත ගොස් ECG පරීක්ෂාවක් සිදුකළ යුතුය.",
        "decreased_interpretation_en": "Normal baseline level. If ischemic chest pain is recurrent, serial repeat testing at 1-3 hours is standard clinical protocol.",
        "decreased_interpretation_si": "සාමාන්‍ය මට්ටමක පවතී. කෙසේ වෙතත් පපුවේ වේදනාවක් ඇත්නම් නැවත පරීක්ෂා කිරීම නිර්දේශ කෙරේ.",
        "related_icd11": ["BA41"]
    },
    "crp": {
        "canonical_id": "crp",
        "aliases": ["crp", "c-reactive protein", "c reactive protein", "සීආර්පී"],
        "display_name_en": "C-Reactive Protein (CRP)",
        "display_name_si": "සී-ප්‍රතික්‍රියාශීලී ප්‍රෝටීන් (CRP)",
        "category": "Inflammatory Biomarkers",
        "unit": "mg/L",
        "ref_min": 0.0,
        "ref_max": 5.0,
        "panic_low": 0.0,
        "panic_high": 100.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated CRP (> 10 mg/L) signals active acute systemic inflammation. Marked elevation (> 100 mg/L) strongly correlates with invasive bacterial infections (pneumonia, sepsis, pyelonephritis) or active vasculitis.",
        "elevated_interpretation_si": "CRP අගය වැඩි වීමෙන් ශරීරය තුළ සක්‍රීය බැක්ටීරියා ආසාදනයක් (Pneumonia, Sepsis) හෝ ප්‍රදාහයක් පවතින බව තහවුරු වේ.",
        "decreased_interpretation_en": "Normal physiological baseline with absence of major systemic acute phase response.",
        "decreased_interpretation_si": "ශරීරය තුළ බරපතල ආසාදන තත්ත්වයක් නොමැති බව පෙන්නුම් කරන සාමාන්‍ය අගයකි.",
        "related_icd11": ["CA40", "GC08", "FA20"]
    },

    # ----------------------------------------------------
    # 7. THYROID FUNCTION PROFILE
    # ----------------------------------------------------
    "tsh": {
        "canonical_id": "tsh",
        "aliases": ["tsh", "thyroid stimulating hormone", "තයිරොයිඩ් ටීඑස්එච්"],
        "display_name_en": "Thyroid Stimulating Hormone (TSH)",
        "display_name_si": "තයිරොයිඩ් හෝමෝන පාලන මට්ටම (TSH)",
        "category": "Thyroid Function Profile",
        "unit": "mIU/L",
        "ref_min": 0.4,
        "ref_max": 4.0,
        "panic_low": 0.01,
        "panic_high": 20.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Elevated TSH (> 4.0 mIU/L) indicates Primary Hypothyroidism (Hashimoto's thyroiditis, iodine deficiency). Symptoms include fatigue, weight gain, cold intolerance, and constipation.",
        "elevated_interpretation_si": "TSH අගය වැඩිවීම තයිරොයිඩ් ග්‍රන්ථියේ ඌන ක්‍රියාකාරීත්වය (Hypothyroidism) පෙන්නුම් කරයි. අධික තෙහෙට්ටුව, බර වැඩිවීම සහ හිසකෙස් වැටීම මෙහි රෝග ලක්ෂණ වේ.",
        "decreased_interpretation_en": "Suppressed TSH (< 0.4 mIU/L) indicates Hyperthyroidism / Thyrotoxicosis (Graves' disease, toxic nodular goiter). Symptoms include palpitations, heat intolerance, tremor, and weight loss.",
        "decreased_interpretation_si": "TSH අගය අඩුවීම තයිරොයිඩ් ග්‍රන්ථියේ අධි ක්‍රියාකාරීත්වය (Hyperthyroidism) පෙන්නුම් කරයි. හෘද ස්පන්දනය වැඩිවීම, අත් වෙව්ලීම සහ අනවශ්‍ය ලෙස බර අඩුවීම ඇතිවිය හැක.",
        "related_icd11": ["5A00", "5A02"]
    },

    # ----------------------------------------------------
    # 8. URINE FULL REPORT (UFR / URINALYSIS)
    # ----------------------------------------------------
    "urine_protein": {
        "canonical_id": "urine_protein",
        "aliases": ["urine protein", "urine albumin", "proteinuria", "albuminuria", "මුත්‍රා ප්‍රෝටීන්"],
        "display_name_en": "Urine Protein / Albumin",
        "display_name_si": "මුත්‍රා වල ප්‍රෝටීන් පැවතීම (Urine Protein)",
        "category": "Urine Full Report (UFR)",
        "unit": "Qualitative",
        "ref_min": 0,
        "ref_max": 0,
        "is_qualitative": True,
        "positive_interpretation_en": "POSITIVE (1+, 2+, 3+, or Trace): Proteinuria indicates glomerular breakdown, diabetic nephropathy, glomerulonephritis, or severe Preeclampsia in pregnant patients.",
        "positive_interpretation_si": "ධනාත්මකයි (POSITIVE): මුත්‍රාවල ප්‍රෝටීන් පිටවීම වකුගඩු ආබාධයක්, දියවැඩියා සංකූලතාවයක් හෝ ගර්භණී සමයේදී අධිරුධිර පීඩනය නිසා ඇතිවන ප්‍රීඑක්ලැම්ප්සියාව (Preeclampsia) පෙන්නුම් කරයි.",
        "negative_interpretation_en": "NEGATIVE / NIL: Normal physiological finding with intact glomerular filtration barrier.",
        "negative_interpretation_si": "සෘණාත්මකයි (NEGATIVE): සාමාන්‍ය නිරෝගී තත්ත්වයකි. වකුගඩු මඟින් ප්‍රෝටීන් කාන්දු වීමක් සිදු නොවේ.",
        "related_icd11": ["GB61", "JA24"]
    },
    "urine_pus_cells": {
        "canonical_id": "urine_pus_cells",
        "aliases": ["pus cells", "urine wbc", "leukocytes urine", "සැරව සෛල"],
        "display_name_en": "Urine Pus Cells (WBC)",
        "display_name_si": "මුත්‍රාවල සැරව සෛල (Urine Pus Cells)",
        "category": "Urine Full Report (UFR)",
        "unit": "/HPF",
        "ref_min": 0.0,
        "ref_max": 5.0,
        "panic_low": 0.0,
        "panic_high": 50.0,
        "is_qualitative": False,
        "elevated_interpretation_en": "Pyuria (> 5 /HPF) is indicative of Urinary Tract Infection (Cystitis, Urethritis, or Pyelonephritis). Urine culture & antimicrobial sensitivity testing is recommended.",
        "elevated_interpretation_si": "සැරව සෛල වැඩිවීම (Pyuria) මුත්‍රා මාර්ගයේ ආසාදනයක් (UTI) පෙන්නුම් කරයි. මුත්‍රා දැවිල්ල, නිතර මුත්‍රා පිටවීම මෙහි ලක්ෂණ වේ. වෛද්‍ය උපදෙස් මත ප්‍රතිජීවක ඖෂධ අවශ්‍ය විය හැක.",
        "decreased_interpretation_en": "Normal physiological finding (< 5 /HPF) excluding active bacterial urinary infection.",
        "decreased_interpretation_si": "සාමාන්‍ය නිරෝගී මට්ටමකි.",
        "related_icd11": ["GC08"]
    }
}

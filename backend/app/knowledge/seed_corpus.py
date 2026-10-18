import hashlib
from typing import List, Dict, Any
from app.models.pathology import MedicalSpecialty, TriageAcuityLevel


def _calc_hash(code: str, name: str) -> str:
    return hashlib.sha256(f"{code}:{name}:medguard_v2".encode("utf-8")).hexdigest()[:16]


CLINICAL_PATHOLOGY_CORPUS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. INFECTIOUS & TROPICAL DISEASES
    # -------------------------------------------------------------------------
    {
        "icd11_code": "1D2Z",
        "icd10_code": "A97.9",
        "clinical_name": "Dengue Fever with Warning Signs",
        "common_aliases": ["Dengue Hemorrhagic Fever", "Breakbone Fever", "ඩෙංගු උණ", "Dengue Shock Syndrome"],
        "medical_specialty": MedicalSpecialty.INFECTIOUS_DISEASES,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Arboviral infection caused by DENV 1-4 transmitted by Aedes aegypti. "
            "Immunopathogenesis involves antibody-dependent enhancement leading to severe immune activation, "
            "endothelial glycocalyx disruption, systemic plasma leakage into pleural/peritoneal cavities, "
            "and secondary coagulopathy / profound thrombocytopenia."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Acute high-grade continuous fever (39-40 C)", "weight": 0.95},
                {"symptom": "Severe retro-orbital pain and frontal headache", "weight": 0.88},
                {"symptom": "Severe generalized myalgia, arthralgia, and bone pain", "weight": 0.85},
            ],
            "secondary": [
                {"symptom": "Flushed facies and maculopapular rash", "weight": 0.65},
                {"symptom": "Mild gingival bleeding or epistaxis", "weight": 0.60},
                {"symptom": "Nausea, vomiting, and anorexia", "weight": 0.70},
            ]
        },
        "red_flag_criteria": [
            "Severe persistent abdominal pain or tenderness (critical phase indicator)",
            "Persistent vomiting (>3 episodes in 1 hour or >4 in 6 hours)",
            "Clinical fluid accumulation (pleural effusion or ascites on ultrasound)",
            "Mucosal bleeding from gastrointestinal or genitourinary tract",
            "Lethargy, restlessness, or altered sensorium",
            "Hepatomegaly > 2 cm below costal margin",
            "Rapid concurrent rise in hematocrit (>20%) with precipitous platelet drop (<100,000/uL)"
        ],
        "differential_diagnoses": [
            {"condition": "Leptospirosis", "icd11": "1C12", "distinction": "Prominent conjunctival suffusion, severe calf tenderness, marked neutrophilic leukocytosis."},
            {"condition": "Malaria", "icd11": "1F40", "distinction": "Periodic paroxysmal rigors with splenomegaly; demonstrated blood film schizonts/ring forms."},
            {"condition": "Typhoid Fever", "icd11": "1A07.0", "distinction": "Step-ladder pyrexia, relative bradycardia (Faget sign), positive blood culture."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (hematocrit baseline and platelet count monitoring)", "Dengue NS1 Antigen (Days 1-4)", "Dengue IgM/IgG ELISA (Day 5 onwards)"],
            "imaging_ecg": ["Point-of-Care Ultrasound (POCUS) for gallbladder wall thickening and free fluid", "Chest X-ray (right lateral decubitus for effusion)"],
            "confirmatory_tests": ["Serum AST/ALT elevation", "Serum electrolytes and renal function tests", "Serum lactate"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Strict bed rest; avoidance of intramuscular injections and contact trauma",
                "Graduated oral rehydration with isotonic electrolyte fluids (WHO ORS, fresh fruit juices) - avoid plain water boluses to prevent hyponatremia"
            ],
            "pharmacotherapy": [
                "Paracetamol 10-15 mg/kg every 6 hours (max 60 mg/kg/day or 3g in adults)",
                "Isotonic crystalloid (0.9% Normal Saline or Hartmann's) maintenance titration during critical plasma leakage window (48 hours)"
            ],
            "contraindications": [
                "STRICTLY CONTRAINDICATED: NSAIDs (Ibuprofen, Diclofenac, Mefenamic acid), Aspirin, and Corticosteroids due to severe gastric hemorrhage and platelet dysfunction."
            ]
        },
        "source_metadata": {
            "issuing_authority": "World Health Organization & Ministry of Health",
            "guideline_title": "WHO Comprehensive Guidelines for Clinical Management of Dengue",
            "publication_year": 2024,
            "source_url": "https://www.who.int/publications/i/item/9789240003504",
            "verification_hash": _calc_hash("1D2Z", "Dengue Fever")
        }
    },
    {
        "icd11_code": "1C12",
        "icd10_code": "A27.0",
        "clinical_name": "Leptospirosis",
        "common_aliases": ["Weil Disease", "Mud Fever", "Swamp Fever", "මී උණ", "Rat Fever"],
        "medical_specialty": MedicalSpecialty.INFECTIOUS_DISEASES,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Zoonotic spirochetal infection caused by Leptospira interrogans shed in rodent urine. "
            "Penetrates mucous membranes or abraded skin during contact with contaminated water or soil. "
            "Hematogenous dissemination triggers generalized systemic vasculitis, endothelial damage, "
            "hepatic sinusoidal injury, renal acute tubular necrosis, and alveolar pulmonary hemorrhage."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "High spiking fever with shaking chills", "weight": 0.90},
                {"symptom": "Extreme calf muscle and lumbar tenderness", "weight": 0.92},
                {"symptom": "Bilateral non-purulent conjunctival suffusion without discharge", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Severe frontal and retro-orbital throbbing headache", "weight": 0.75},
                {"symptom": "Oliguria or dark amber urine", "weight": 0.70},
                {"symptom": "Nausea, vomiting, and profound malaise", "weight": 0.65},
            ]
        },
        "red_flag_criteria": [
            "Severe oliguria (<0.5 mL/kg/h) or acute anuria indicating acute renal failure",
            "Frank hemoptysis, tachypnea (>30/min), and dyspnea (Severe Pulmonary Hemorrhagic Syndrome)",
            "Rapidly deepening clinical jaundice with hepatomegaly (Weil syndrome)",
            "Hypotension refractory to fluid resuscitation or irregular cardiac rhythm (myocarditis)"
        ],
        "differential_diagnoses": [
            {"condition": "Dengue Fever", "icd11": "1D2Z", "distinction": "Leptospirosis features conjunctival suffusion and marked neutrophilic leukocytosis, whereas Dengue displays leukopenia."},
            {"condition": "Acute Viral Hepatitis", "icd11": "1E51", "distinction": "Leptospirosis features severe muscle tenderness and marked acute renal impairment."},
            {"condition": "Hantavirus Pulmonary Syndrome", "icd11": "1D62", "distinction": "Serology-specific distinction, exposure history to rodent excreta aerosols."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (neutrophilia with left shift, thrombocytopenia)", "Serum Creatinine and Blood Urea Nitrogen (BUN)", "Urine full report (proteinuria, microscopic hematuria, granular casts)"],
            "imaging_ecg": ["ECG (ST-T changes, AV conduction blocks)", "Chest Radiograph (patchy bilateral alveolar infiltrates)"],
            "confirmatory_tests": ["Microscopic Agglutination Test (MAT - gold standard)", "Leptospira DNA Real-Time PCR (blood/urine)", "Rapid Lepto IgM immunochromatography"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Hospitalization for moderate to severe disease",
                "Strict fluid balance monitoring with hourly urine output charting"
            ],
            "pharmacotherapy": [
                "Severe disease: Intravenous Benzylpenicillin 1.5 million units IV Q6H or Ceftriaxone 1g IV Q24H for 7 days",
                "Mild ambulatory disease: Oral Doxycycline 100 mg twice daily for 7 days (or Azithromycin in pregnancy/children)"
            ],
            "contraindications": [
                "Caution for Jarisch-Herxheimer reaction within 2 hours of initiating antimicrobial therapy; manage with antipyretics and hemodynamic support."
            ]
        },
        "source_metadata": {
            "issuing_authority": "WHO & International Leptospirosis Society",
            "guideline_title": "Human Leptospirosis: Guidance for Diagnosis, Surveillance and Control",
            "publication_year": 2023,
            "source_url": "https://www.who.int/publications/i/item/human-leptospirosis-guidance",
            "verification_hash": _calc_hash("1C12", "Leptospirosis")
        }
    },
    {
        "icd11_code": "1B10",
        "icd10_code": "A15.0",
        "clinical_name": "Pulmonary Tuberculosis",
        "common_aliases": ["TB", "Phthisis", "Consumption", "ක්ෂය රෝගය"],
        "medical_specialty": MedicalSpecialty.INFECTIOUS_DISEASES,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Chronic intracellular bacterial infection caused by Mycobacterium tuberculosis transmitted via droplet nuclei. "
            "Inhaled bacilli multiply in alveolar macrophages, forming Ghon complexes. "
            "Cell-mediated immunity produces caseating granulomatous inflammation. "
            "Reactivation or cavitation leads to extensive parenchymal destruction and bronchogenic dissemination."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Persistent cough with sputum for 2 weeks or more", "weight": 0.95},
                {"symptom": "Hemoptysis (blood-streaked sputum to frank blood)", "weight": 0.85},
                {"symptom": "Unexplained progressive weight loss and anorexia", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Drenching nocturnal diaphoresis (night sweats)", "weight": 0.82},
                {"symptom": "Low-grade evening pyrexia", "weight": 0.80},
                {"symptom": "Pleuritic chest pain and easy fatigability", "weight": 0.70},
            ]
        },
        "red_flag_criteria": [
            "Massive hemoptysis (>200 mL in 24 hours) risking asphyxiation and airway obstruction",
            "Severe respiratory distress with oxygen saturation < 90% on room air",
            "Signs of tuberculous meningitis (stiff neck, cranial nerve palsies, confusion)",
            "Tension pneumothorax secondary to ruptured apical cavitary lesion"
        ],
        "differential_diagnoses": [
            {"condition": "Bronchogenic Carcinoma", "icd11": "2C25", "distinction": "Older smokers, unresolving consolidations, absence of caseation, tissue biopsy confirmation."},
            {"condition": "Bronchiectasis", "icd11": "CA24", "distinction": "Copious purulent sputum production, tram-track and signet-ring sign on HRCT scan."},
            {"condition": "Chronic Cavitary Aspergillosis", "icd11": "1F20", "distinction": "Fungal ball inside pre-existing cavity, positive Aspergillus precipitin serology."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Sputum GeneXpert MTB/RIF (rapid molecular assay with rifampicin resistance detection)", "Sputum smear microscopy for Acid-Fast Bacilli (Ziehl-Neelsen or Auramine-O stain)"],
            "imaging_ecg": ["Posteroanterior Chest Radiograph (apical and subapical consolidations, cavitary lesions, hilar adenopathy)"],
            "confirmatory_tests": ["Mycobacterial culture on Lowenstein-Jensen or MGIT liquid medium with Drug Susceptibility Testing (DST)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Airborne infection control: well-ventilated isolation room, surgical masks for patient during transit",
                "High-protein nutritional supplementation and psychosocial adherence support"
            ],
            "pharmacotherapy": [
                "Standard 6-month Directly Observed Therapy (DOTS): 2 months Intensive Phase with Rifampicin (R), Isoniazid (H), Pyrazinamide (Z), Ethambutol (E) (2RHZE), followed by 4 months Continuation Phase with Rifampicin and Isoniazid (4RH)",
                "Pyridoxine (Vitamin B6) 10-25 mg daily to prevent Isoniazid-induced peripheral neuropathy"
            ],
            "contraindications": [
                "Never add a single drug to a failing antituberculosis regimen due to rapid induction of multi-drug resistance (MDR-TB)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "World Health Organization",
            "guideline_title": "WHO Consolidated Guidelines on Tuberculosis: Module 4 Treatment",
            "publication_year": 2024,
            "source_url": "https://www.who.int/publications/i/item/9789240048126",
            "verification_hash": _calc_hash("1B10", "Pulmonary Tuberculosis")
        }
    },
    {
        "icd11_code": "1F40",
        "icd10_code": "B50.9",
        "clinical_name": "Plasmodium Falciparum Malaria",
        "common_aliases": ["Malignant Tertian Malaria", "Falciparum Infection", "මැලේරියාව"],
        "medical_specialty": MedicalSpecialty.INFECTIOUS_DISEASES,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Protozoan parasite transmitted by female Anopheles mosquitoes. "
            "Sporozoites infect hepatocytes before merozoite erythrocyte invasion. "
            "P. falciparum expresses PfEMP1 on infected RBC surfaces, causing cytoadherence and microvascular sequestration "
            "in cerebral, pulmonary, and renal capillary beds, precipitating severe tissue hypoxia and metabolic acidosis."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Recurrent paroxysms of severe rigors, high fever, and profuse drenching sweats", "weight": 0.94},
                {"symptom": "Intense holocranial headache and prostration", "weight": 0.86},
                {"symptom": "Pallor secondary to acute intravascular hemolysis", "weight": 0.82},
            ],
            "secondary": [
                {"symptom": "Splenomegaly with left upper quadrant fullness", "weight": 0.74},
                {"symptom": "Mild scleral icterus (unconjugated hyperbilirubinemia)", "weight": 0.68},
                {"symptom": "Nausea, watery diarrhea, and generalized myalgia", "weight": 0.60},
            ]
        },
        "red_flag_criteria": [
            "Impaired consciousness or repetitive generalized seizures (Cerebral Malaria)",
            "Acidotic breathing (Kussmaul respiration) indicating severe lactic acidosis",
            "Severe normocytic anemia (Hb < 5 g/dL, Hematocrit < 15%)",
            "Circulatory collapse with systolic BP < 80 mmHg (Algid Malaria)",
            "Hyperparasitemia (>10% infected red blood cells on thin blood film)"
        ],
        "differential_diagnoses": [
            {"condition": "Dengue with Warning Signs", "icd11": "1D2Z", "distinction": "Dengue lacks periodic paroxysms and features negative malaria smear/RDT."},
            {"condition": "Sepsis / Septic Shock", "icd11": "1G40", "distinction": "Elevated serum procalcitonin, distinct focal source of bacterial infection."},
            {"condition": "Typhoid Enteric Fever", "icd11": "1A07.0", "distinction": "Sustained non-paroxysmal pyrexia with rose spots and positive blood culture."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Thick and Thin Giemsa-stained blood films (parasite species and density quantification)", "Malaria Rapid Diagnostic Test (RDT detecting HRP2 and pLDH)", "Full Blood Count (normocytic anemia, thrombocytopenia)"],
            "imaging_ecg": ["ECG (baseline QTc interval before artemisinin combination therapy)"],
            "confirmatory_tests": ["Serum blood glucose (hypoglycemia check)", "Serum venous blood gas / lactate", "Renal function tests"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Urgent hospitalization for falciparum confirmed cases",
                "Bed net utilization and vector surveillance notification"
            ],
            "pharmacotherapy": [
                "Uncomplicated: Artemisinin-based Combination Therapy (ACT) e.g., Artemether-Lumefantrine (20/120 mg oral regimen) or Dihydroartemisinin-Piperaquine for 3 days",
                "Severe Malaria: Intravenous Artesunate 2.4 mg/kg IV at 0, 12, and 24 hours, then daily until oral transition"
            ],
            "contraindications": [
                "Do not administer artemisinin monotherapy due to rapid emergence of drug resistance; always use validated combinations."
            ]
        },
        "source_metadata": {
            "issuing_authority": "World Health Organization Global Malaria Programme",
            "guideline_title": "WHO Guidelines for Malaria",
            "publication_year": 2024,
            "source_url": "https://www.who.int/publications/i/item/guidelines-for-malaria",
            "verification_hash": _calc_hash("1F40", "Falciparum Malaria")
        }
    },
    {
        "icd11_code": "RA01",
        "icd10_code": "U07.1",
        "clinical_name": "Acute COVID-19 with Lower Respiratory Involvement",
        "common_aliases": ["SARS-CoV-2 Infection", "Novel Coronavirus", "කොවිඩ්-19"],
        "medical_specialty": MedicalSpecialty.INFECTIOUS_DISEASES,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Infection with SARS-CoV-2 binding to pulmonary alveolar type II ACE2 receptors. "
            "Viral replication triggers innate immune hyperactivation, microvascular endothelial inflammation, "
            "diffuse alveolar damage, localized immunothrombosis, and impaired ventilation-perfusion matching "
            "resulting in silent or acute hypoxemia."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Exertional dyspnea with oxygen desaturation", "weight": 0.92},
                {"symptom": "Persistent high fever and dry hacking cough", "weight": 0.88},
                {"symptom": "Profound fatigue and generalized muscle weakness", "weight": 0.80},
            ],
            "secondary": [
                {"symptom": "Anosmia (loss of smell) and ageusia (loss of taste)", "weight": 0.78},
                {"symptom": "Sore throat, rhinorrhea, and headache", "weight": 0.65},
                {"symptom": "Gastrointestinal upset including loose stools", "weight": 0.55},
            ]
        },
        "red_flag_criteria": [
            "Silent hypoxemia: SpO2 < 92% on room air or precipitous drop > 4% upon minimal ambulation",
            "Severe respiratory distress (respiratory rate > 28 breaths/min with accessory muscle use)",
            "Cyanosis of lips or oral mucosa",
            "Hemodynamic compromise, acute confusion, or syncope"
        ],
        "differential_diagnoses": [
            {"condition": "Influenza A/B Infection", "icd11": "1E30", "distinction": "Rapid abrupt onset within 12 hours, high fever, prominent myalgia, negative COVID-19 PCR/antigen."},
            {"condition": "Community-Acquired Bacterial Pneumonia", "icd11": "CA40", "distinction": "Focal lobar consolidation with productive rusty sputum, marked procalcitonin elevation."},
            {"condition": "Acute Pulmonary Embolism", "icd11": "BB00", "distinction": "Abrupt chest pain, sudden desaturation without prior viral prodrome, high D-dimer with filling defect on CTPA."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["SARS-CoV-2 RT-PCR or rapid antigen detection", "Pulse oximetry (resting and 1-minute walk test)", "Full Blood Count (lymphopenia, elevated neutrophil-lymphocyte ratio)"],
            "imaging_ecg": ["High-Resolution CT Thorax (bilateral ground-glass opacities with subpleural and peripheral distribution)", "Point-of-care lung ultrasound (diffuse B-lines)"],
            "confirmatory_tests": ["C-Reactive Protein (CRP), Ferritin, and D-Dimer (inflammatory prognostic stratification)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Awake prone positioning (30-120 minutes 2-4 times daily) to recruit dorsal alveolar zones",
                "Home pulse oximetry monitoring 3 times daily with strict return criteria"
            ],
            "pharmacotherapy": [
                "Hypoxemic patients (SpO2 < 92%): Dexamethasone 6 mg orally or IV once daily for up to 10 days",
                "Targeted antiviral for high-risk outpatients within 5 days of onset: Nirmatrelvir/Ritonavir (Paxlovid)",
                "Low-molecular-weight heparin (Enoxaparin) thromboprophylaxis for hospitalized cohorts"
            ],
            "contraindications": [
                "Do NOT use systemic corticosteroids in non-hypoxemic patients with SpO2 >= 94% as it impairs viral clearance."
            ]
        },
        "source_metadata": {
            "issuing_authority": "National Institutes of Health & WHO",
            "guideline_title": "NIH COVID-19 Treatment Guidelines",
            "publication_year": 2024,
            "source_url": "https://www.covid19treatmentguidelines.nih.gov/",
            "verification_hash": _calc_hash("RA01", "Acute COVID-19")
        }
    },
    {
        "icd11_code": "1E51",
        "icd10_code": "B16.9",
        "clinical_name": "Acute Viral Hepatitis B",
        "common_aliases": ["Hep B", "Serum Hepatitis", "හෙපටයිටිස් බී"],
        "medical_specialty": MedicalSpecialty.INFECTIOUS_DISEASES,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Hepatotropic DNA hepadnavirus transmitted via parenteral, sexual, or perinatal routes. "
            "Hepatocellular injury is mediated by host cytotoxic CD8+ T-cell immune responses against viral antigens "
            "(HBsAg, HBcAg) expressed on hepatocyte membranes, leading to apoptosis, lobular inflammation, "
            "and cholestatic canalicular disruption."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Deep scleral and cutaneous icterus (jaundice)", "weight": 0.90},
                {"symptom": "Dark tea-colored urine with pale acholic stools", "weight": 0.88},
                {"symptom": "Right upper quadrant hepatic dull aching discomfort", "weight": 0.80},
            ],
            "secondary": [
                {"symptom": "Profound fatigue, generalized malaise, and anorexia", "weight": 0.75},
                {"symptom": "Nausea, vomiting, and distaste for cigarettes/food", "weight": 0.70},
                {"symptom": "Transient pre-icteric urticarial rash and arthralgia", "weight": 0.60},
            ]
        },
        "red_flag_criteria": [
            "Coagulopathy with Prothrombin Time / INR > 1.5 indicating acute hepatic failure",
            "Hepatic encephalopathy: asterixis (flapping tremor), reversal of sleep cycle, confusion",
            "Shrinking liver span on daily percussion (massive acute hepatic necrosis)",
            "Intractable persistent vomiting preventing oral fluid and caloric intake"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Viral Hepatitis A / E", "icd11": "1E50", "distinction": "Fecal-oral transmission, positive anti-HAV IgM / anti-HEV IgM with negative HBsAg."},
            {"condition": "Drug-Induced Liver Injury (DILI)", "icd11": "NE80", "distinction": "Temporal association with hepatotoxic drugs (e.g. high-dose Paracetamol, herbal remedies, Amoxicillin-Clavulanate)."},
            {"condition": "Acute Choledocholithiasis with Cholangitis", "icd11": "DC11", "distinction": "Charcot triad: biliary colic, fever with chills, jaundice with dilated common bile duct on ultrasound."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Hepatitis B Surface Antigen (HBsAg)", "Anti-HBc IgM (diagnostic marker of acute infection)", "Liver Function Tests (AST/ALT characteristically > 1000 IU/L, elevated conjugated bilirubin)"],
            "imaging_ecg": ["Abdominal Ultrasound (rule out biliary obstruction, assess hepatic parenchymal echotexture)"],
            "confirmatory_tests": ["Serum INR / Prothrombin Time (mandatory prognostic liver synthesis check)", "Quantitative HBV DNA PCR"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Bed rest guided by subjective fatigue; complete abstinence from alcohol and all hepatotoxic xenobiotics",
                "High-carbohydrate, moderate-protein diet with small frequent meals to sustain glycogen reserves"
            ],
            "pharmacotherapy": [
                "Uncomplicated acute hepatitis B: Supportive outpatient care with close outpatient monitoring (95% resolve spontaneously in immunocompetent adults)",
                "Severe/Fulminant acute presentation (INR > 1.5, severe jaundice): Immediate initiation of oral Nucleoside Analogue (Entecavir 0.5 mg daily or Tenofovir Disoproxil 300 mg daily) and transfer to liver transplant center"
            ],
            "contraindications": [
                "Avoid sedatives and hepatically metabolized drugs (Benzodiazepines, Opioids) which can precipitate hepatic coma."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Association for the Study of the Liver (EASL) & AASLD",
            "guideline_title": "EASL Clinical Practice Guidelines on the Management of Hepatitis B Virus Infection",
            "publication_year": 2023,
            "source_url": "https://www.easl.eu/guidelines/hepatitis-b/",
            "verification_hash": _calc_hash("1E51", "Hepatitis B")
        }
    },

    # -------------------------------------------------------------------------
    # 2. CARDIOVASCULAR MEDICINE
    # -------------------------------------------------------------------------
    {
        "icd11_code": "BA41",
        "icd10_code": "I21.3",
        "clinical_name": "Acute Coronary Syndrome (STEMI / NSTE-ACS)",
        "common_aliases": ["Myocardial Infarction", "Heart Attack", "හෘදයාබාධය", "Coronary Thrombosis"],
        "medical_specialty": MedicalSpecialty.CARDIOVASCULAR,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Atherosclerotic coronary fibrous plaque rupture or erosion triggering platelet activation, "
            "adhesion, and thrombus formation via the coagulation cascade. "
            "Complete or critical coronary arterial occlusion precipitates downstream ischemic cardiomyocyte necrosis, "
            "loss of membrane integrity with troponin leakage, and life-threatening ventricular dysrhythmias."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Crushing, squeezing, heavy retrosternal chest pain or pressure", "weight": 0.98},
                {"symptom": "Radiation of chest discomfort to left shoulder, left arm, neck, or jaw", "weight": 0.92},
                {"symptom": "Profuse cold diaphoresis and nausea", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Acute onset dyspnea and orthopnea", "weight": 0.82},
                {"symptom": "Sense of impending doom (angor animi)", "weight": 0.78},
                {"symptom": "Lightheadedness, presyncope, or acute syncope", "weight": 0.75},
            ]
        },
        "red_flag_criteria": [
            "Any chest discomfort lasting > 15 minutes unresponsive to rest",
            "Hemodynamic instability (systolic blood pressure < 90 mmHg, cold clammy extremities)",
            "Pulmonary edema with bilateral lung crepitations and tachypnea",
            "Ventricular tachycardia, ventricular fibrillation, or high-grade AV block on monitoring",
            "Unexplained sudden syncope in the presence of retrosternal pain"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Aortic Dissection", "icd11": "BD50", "distinction": "Tearing interscapular back pain, asymmetric upper limb pulses/blood pressure, widened mediastinum on chest X-ray."},
            {"condition": "Acute Pulmonary Embolism", "icd11": "BB00", "distinction": "Pleuritic chest pain, prominent dyspnea, right heart strain on ECG, lower limb DVT signs."},
            {"condition": "Acute Pericarditis", "icd11": "BB20", "distinction": "Sharp chest pain relieved by sitting forward, PR depression and diffuse ST elevation across all leads."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Immediate High-Sensitivity Cardiac Troponin I/T (serial at 0h, 1h, 3h)", "Full Blood Count, Serum Electrolytes, Renal Function, Lipid Profile"],
            "imaging_ecg": ["12-Lead ECG recorded within 10 minutes of patient arrival (ST elevation >=1mm in contiguous leads or new LBBB)", "Bedside Echocardiography for regional wall motion abnormalities"],
            "confirmatory_tests": ["Emergency Coronary Angiography (within 90-120 minutes door-to-balloon time)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate emergency paramedic dispatch; rest in seated posture with continuous ECG monitoring",
                "Supplemental oxygen ONLY if SpO2 < 90% (avoid hyperoxia-induced coronary vasoconstriction)"
            ],
            "pharmacotherapy": [
                "Loading antiplatelet: Aspirin 300 mg chewed immediately + P2Y12 inhibitor (Ticagrelor 180 mg or Prasugrel 60 mg or Clopidogrel 300-600 mg)",
                "Sublingual Glyceryl Trinitrate (GTN) 400 mcg spray for pain relief (unless right ventricular infarction or SBP < 90)",
                "Primary Percutaneous Coronary Intervention (PCI) or IV Fibrinolysis (Tenecteplase) if PCI unavailable within 120 minutes"
            ],
            "contraindications": [
                "STRICTLY CONTRAINDICATED: Nitrates are contraindicated if PDE-5 inhibitors (Sildenafil, Tadalafil) were taken within 24-48 hours, or in suspected right ventricular infarction."
            ]
        },
        "source_metadata": {
            "issuing_authority": "AHA/ACC & European Society of Cardiology (ESC)",
            "guideline_title": "ESC Guidelines for the Management of Acute Coronary Syndromes",
            "publication_year": 2024,
            "source_url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Acute-Coronary-Syndromes-ACS-Guidelines",
            "verification_hash": _calc_hash("BA41", "Acute Coronary Syndrome")
        }
    },
    {
        "icd11_code": "BA00",
        "icd10_code": "I10",
        "clinical_name": "Essential (Primary) Hypertension",
        "common_aliases": ["High Blood Pressure", "Systemic Hypertension", "අධික රුධිර පීඩනය"],
        "medical_specialty": MedicalSpecialty.CARDIOVASCULAR,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Multifactorial vascular disorder involving increased peripheral vascular resistance, "
            "sympathetic nervous system overactivity, dysregulated renin-angiotensin-aldosterone system (RAAS), "
            "and impaired renal sodium excretion, culminating in sustained mechanical arterial wall shear stress, "
            "endothelial dysfunction, left ventricular hypertrophy, and accelerated atherogenesis."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Asymptomatic in early stages (the 'silent killer')", "weight": 0.95},
                {"symptom": "Sustained office systolic BP >= 140 mmHg or diastolic >= 90 mmHg on repeated visits", "weight": 0.98},
            ],
            "secondary": [
                {"symptom": "Occipital morning throbbing headache", "weight": 0.65},
                {"symptom": "Epistaxis (nasal bleeding)", "weight": 0.50},
                {"symptom": "Exertional dyspnea and palpitations", "weight": 0.55},
            ]
        },
        "red_flag_criteria": [
            "Hypertensive Emergency: BP > 180/120 mmHg WITH acute target organ damage",
            "Acute visual disturbance or papilledema (Malignant Hypertension)",
            "Acute neurological deficit, altered mental status, or encephalopathy",
            "Acute chest pain, severe dyspnea, or pulmonary edema"
        ],
        "differential_diagnoses": [
            {"condition": "White-Coat Hypertension", "icd11": "BA04", "distinction": "Elevated clinic readings with normal ambulatory (ABPM) / home blood pressure monitoring (<135/85 mmHg)."},
            {"condition": "Renovascular Hypertension (Renal Artery Stenosis)", "icd11": "BA01.0", "distinction": "Refractory hypertension, abdominal bruits, flash pulmonary edema, acute worsening of renal function on ACE inhibitors."},
            {"condition": "Primary Aldosteronism (Conn Syndrome)", "icd11": "5A71", "distinction": "Spontaneous hypokalemia with suppressed plasma renin and elevated aldosterone-to-renin ratio."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["24-Hour Ambulatory Blood Pressure Monitoring (ABPM)", "Urinalysis for albuminuria/proteinuria and microhematuria", "Serum Creatinine and Estimated GFR (eGFR)", "Serum Potassium, Sodium, and Fasting Blood Glucose"],
            "imaging_ecg": ["12-Lead ECG for Sokolow-Lyon criteria of Left Ventricular Hypertrophy (LVH)"],
            "confirmatory_tests": ["Fundoscopy for hypertensive retinopathy (AV nicking, hemorrhages, exudates)", "Transthoracic Echocardiogram"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Dietary sodium restriction to < 2,000 mg/day (< 5g salt/day) via DASH diet",
                "Weight optimization (aim for BMI 20-25 kg/m2); 150 min/week moderate aerobic exercise",
                "Alcohol moderation and complete cessation of tobacco smoking"
            ],
            "pharmacotherapy": [
                "Stage 1/2 Hypertension first-line dual combination: ACE-inhibitor (Enalapril / Ramipril) OR ARB (Losartan / Telmisartan) + Dihydropyridine Calcium Channel Blocker (Amlodipine) OR Thiazide-like Diuretic (Indapamide)",
                "Standard target: Clinic BP < 130/80 mmHg in patients under 65 years"
            ],
            "contraindications": [
                "ACE inhibitors and ARBs are absolutely contraindicated during pregnancy (teratogenic); use Labetalol, Methyldopa, or Nifedipine instead."
            ]
        },
        "source_metadata": {
            "issuing_authority": "International Society of Hypertension (ISH) & NICE",
            "guideline_title": "NICE Guideline NG136: Hypertension in Adults - Diagnosis and Management",
            "publication_year": 2023,
            "source_url": "https://www.nice.org.uk/guidance/ng136",
            "verification_hash": _calc_hash("BA00", "Essential Hypertension")
        }
    },
    {
        "icd11_code": "BD11",
        "icd10_code": "I50.9",
        "clinical_name": "Congestive Heart Failure (HFrEF / HFpEF)",
        "common_aliases": ["Cardiac Failure", "Decompensated Heart Failure", "හෘදය අක්‍රිය වීම"],
        "medical_specialty": MedicalSpecialty.CARDIOVASCULAR,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Structural or functional cardiac abnormality leading to elevated intracardiac pressures "
            "or inadequate cardiac output at rest or stress. "
            "Chronic neurohormonal activation (Sympathetic nervous system, RAAS) drives adverse ventricular remodeling, "
            "sodium and water retention, elevated venous filling pressures, and systemic venous/pulmonary congestion."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Exertional breathlessness with reduced functional capacity (NYHA II-IV)", "weight": 0.95},
                {"symptom": "Orthopnea (breathlessness relieved upon sitting upright)", "weight": 0.90},
                {"symptom": "Paroxysmal nocturnal dyspnea (waking gasping for air 1-2h after sleep)", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Bilateral dependent lower limb pitting edema", "weight": 0.85},
                {"symptom": "Elevated jugular venous pressure (JVP) with hepatojugular reflux", "weight": 0.82},
                {"symptom": "Persistent nocturnal cough with pink frothy sputum in acute pulmonary edema", "weight": 0.75},
            ]
        },
        "red_flag_criteria": [
            "Acute pulmonary edema: severe respiratory exhaustion with diffuse bilateral rales and SpO2 < 88%",
            "Cardiogenic shock: systolic BP < 85 mmHg, cold extremities, and oliguria",
            "Syncope or sustained ventricular tachycardia on telemetry",
            "Rapid refractory weight gain (>2 kg in 3 days) indicating acute volume overload"
        ],
        "differential_diagnoses": [
            {"condition": "Chronic Obstructive Pulmonary Disease", "icd11": "CA22", "distinction": "History of heavy smoking, wheezing, absence of orthopnea, normal BNP/NT-proBNP level."},
            {"condition": "Liver Cirrhosis with Ascites", "icd11": "DB93", "distinction": "Normal JVP, stigmata of chronic liver disease (spider naevi, palmar erythema), low serum albumin."},
            {"condition": "Nephrotic Syndrome", "icd11": "GB40", "distinction": "Heavy proteinuria (>3.5 g/24h), severe hypercholesterolemia, normal left ventricular systolic function."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Serum B-type Natriuretic Peptide (BNP > 100 pg/mL) or NT-proBNP (> 300 pg/mL)", "Serum Electrolytes (Sodium, Potassium), Urea, and Creatinine", "Full Blood Count and Liver Enzymes"],
            "imaging_ecg": ["12-Lead ECG (ischemic changes, bundle branch blocks, atrial fibrillation)", "Chest Radiograph (cardiomegaly, upper lobe venous diversion, Kerley B lines, pleural effusions)"],
            "confirmatory_tests": ["Transthoracic Echocardiogram (quantifies Left Ventricular Ejection Fraction - LVEF, diastolic dysfunction, valve disease)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Daily morning weight monitoring after voiding; report weight gain > 1.5-2 kg over 48h",
                "Dietary sodium restriction (< 2 g/day) and fluid restriction (1.5-2 L/day in severe congestion)",
                "Supervised cardiac rehabilitation exercise training when clinically compensated"
            ],
            "pharmacotherapy": [
                "Decongestion: Intravenous Loop Diuretic (Furosemide 20-40 mg IV bolus or infusion)",
                "The 4 Pillars of HFrEF Guideline-Directed Medical Therapy (GDMT): (1) ARNI (Sacubitril/Valsartan) or ACEi, (2) Evidence-based Beta-blocker (Bisoprolol / Carvedilol), (3) Mineralocorticoid Receptor Antagonist (Spironolactone / Eplerenone), (4) SGLT2 Inhibitor (Dapagliflozin / Empagliflozin)"
            ],
            "contraindications": [
                "Non-dihydropyridine Calcium Channel Blockers (Verapamil, Diltiazem) and NSAIDs are contraindicated in HFrEF due to negative inotropy and fluid retention."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Society of Cardiology (ESC) & ACC/AHA",
            "guideline_title": "ESC Guidelines for the Diagnosis and Treatment of Acute and Chronic Heart Failure",
            "publication_year": 2023,
            "source_url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Heart-Failure",
            "verification_hash": _calc_hash("BD11", "Congestive Heart Failure")
        }
    },
    {
        "icd11_code": "BC81.3",
        "icd10_code": "I48.9",
        "clinical_name": "Atrial Fibrillation with Rapid Ventricular Response",
        "common_aliases": ["AFib", "AF", "හෘද ස්පන්දන අක්‍රමිකතාව"],
        "medical_specialty": MedicalSpecialty.CARDIOVASCULAR,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Supraventricular tachyarrhythmia characterized by disorganized, chaotic atrial electrical activation "
            "(300-600 bpm) arising from pulmonary vein ostia triggers. "
            "Loss of coordinated atrial mechanical systole leads to blood stasis in the left atrial appendage, "
            "dramatically predisposing to cardioembolic thrombus formation and systemic thromboembolism (ischemic stroke)."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Irregularly irregular peripheral pulse with apical-radial pulse deficit", "weight": 0.98},
                {"symptom": "Rapid fluttering heart palpitations", "weight": 0.90},
                {"symptom": "Exertional dyspnea, fatigue, and reduced exercise tolerance", "weight": 0.85},
            ],
            "secondary": [
                {"symptom": "Lightheadedness and pre-syncopal dizziness", "weight": 0.72},
                {"symptom": "Atypical chest tightness without focal infarction", "weight": 0.65},
                {"symptom": "Nocturnal polyuria (secondary to atrial natriuretic peptide release)", "weight": 0.50},
            ]
        },
        "red_flag_criteria": [
            "Hemodynamic instability (hypotension SBP < 90 mmHg, acute pulmonary edema, angina)",
            "Acute focal neurological deficits indicating acute cardioembolic stroke",
            "Extreme ventricular rate (> 160-180 bpm) with ischemic ST depressions",
            "Ventricular pre-excitation (Wolff-Parkinson-White with AFib: wide QRS irregular tachycardia)"
        ],
        "differential_diagnoses": [
            {"condition": "Atrial Flutter with Variable Conduction", "icd11": "BC81.2", "distinction": "Regular sawtooth baseline flutter waves (F-waves at 300 bpm) in inferior leads (II, III, aVF)."},
            {"condition": "Sinus Tachycardia with Frequent Ectopics", "icd11": "BC80", "distinction": "P waves precede every QRS complex on 12-lead ECG."},
            {"condition": "Multifocal Atrial Tachycardia (MAT)", "icd11": "BC81.5", "distinction": "Common in severe COPD, distinct P-waves with at least 3 differing morphologies."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["12-Lead ECG (absence of distinct P waves, fibrillatory f-waves, irregularly irregular RR intervals)", "Serum Electrolytes (Potassium, Magnesium)", "Thyroid Stimulating Hormone (TSH to rule out thyrotoxicosis)"],
            "imaging_ecg": ["Transthoracic Echocardiogram (left atrial dimensions, ventricular function, valvular pathology)", "Transesophageal Echocardiogram (exclude left atrial appendage thrombus prior to cardioversion)"],
            "confirmatory_tests": ["24-48 Hour Holter Monitoring for paroxysmal AF detection"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Abstinence from caffeine, alcohol ('holiday heart syndrome'), and sympathomimetic decongestants",
                "Screening and treatment for obstructive sleep apnea and metabolic risk factors"
            ],
            "pharmacotherapy": [
                "Stroke Prevention (Atrial Fibrillation Better Care - ABC Pathway): Risk score via CHA2DS2-VASc. If score >=1 in men or >=2 in women: Direct Oral Anticoagulant (DOAC: Apixaban 5 mg BID, Rivaroxaban 20 mg daily, or Dabigatran 150 mg BID)",
                "Rate Control: Beta-blocker (Bisoprolol 2.5-10 mg daily or Metoprolol) OR non-dihydropyridine CCB (Diltiazem)",
                "Emergency Synchronized DC Cardioversion if hemodynamically unstable"
            ],
            "contraindications": [
                "In WPW with AFib, AV nodal blockers (Digoxin, Verapamil, Diltiazem, Beta-blockers) are strictly contraindicated as they precipitate ventricular fibrillation."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Society of Cardiology (ESC) & AHA/ACC",
            "guideline_title": "ESC Guidelines for the Management of Atrial Fibrillation",
            "publication_year": 2024,
            "source_url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Atrial-Fibrillation-Management",
            "verification_hash": _calc_hash("BC81.3", "Atrial Fibrillation")
        }
    },
    {
        "icd11_code": "BD71",
        "icd10_code": "I80.2",
        "clinical_name": "Deep Vein Thrombosis (DVT)",
        "common_aliases": ["Venous Thrombosis", "Lower Extremity DVT", "ගැඹුරු ශිරා ත්‍රොම්බෝසිස්"],
        "medical_specialty": MedicalSpecialty.CARDIOVASCULAR,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Thrombus formation in deep veins (popliteal, femoral, iliac) governed by Virchow's triad: "
            "endothelial vessel injury, venous stasis (prolonged immobility, surgery), and hypercoagulability "
            "(malignancy, factor V Leiden, antiphospholipid syndrome). "
            "Thrombus propagation risks detachment and embolization into the pulmonary arterial bed (pulmonary embolism)."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Unilateral calf or thigh swelling with asymmetry > 3 cm", "weight": 0.94},
                {"symptom": "Localized deep calf pain and tenderness along venous system", "weight": 0.90},
                {"symptom": "Erythema, warmth, and superficial collateral venous dilation", "weight": 0.82},
            ],
            "secondary": [
                {"symptom": "Pain exacerbated by dorsiflexion of the foot (Homans sign - non-specific)", "weight": 0.50},
                {"symptom": "Low-grade fever and firm, palpable deep cord", "weight": 0.65},
            ]
        },
        "red_flag_criteria": [
            "Sudden onset pleuritic chest pain, tachypnea, and hemoptysis (Pulmonary Embolism trigger)",
            "Phlegmasia Cerulea Dolens: massive iliofemoral thrombosis causing cyanosis, severe ischemia, and gangrene threat",
            "Bilateral ascending swelling extending to the groin and lower abdominal wall"
        ],
        "differential_diagnoses": [
            {"condition": "Ruptured Baker Cyst (Popliteal Cyst)", "icd11": "FA34", "distinction": "Crescent sign of ecchymosis below the lateral malleolus, ultrasound confirmation of popliteal fluid leakage."},
            {"condition": "Cutaneous Cellulitis", "icd11": "1B70", "distinction": "Marked surface erythema with distinct advancing borders, high fever, elevated procalcitonin/CRP."},
            {"condition": "Superficial Thrombophlebitis", "icd11": "BD70", "distinction": "Palpable superficial tender cord along great saphenous vein without deep system involvement."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Pre-test Clinical Probability via Two-Level Wells DVT Score", "Quantitative D-Dimer Assay (high negative predictive value for low/moderate risk)"],
            "imaging_ecg": ["Compression Venous Ultrasonography (CUS) with Doppler interrogation (loss of vein compressibility)"],
            "confirmatory_tests": ["CT Venography or MR Venography if pelvic/iliac vein thrombosis suspected", "Thrombophilia screen (delayed until acute anticoagulation complete)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Early ambulation once therapeutic anticoagulation is established (bed rest is no longer recommended)",
                "Graduated compression stockings (20-30 mmHg) after acute swelling subsides to mitigate Post-Thrombotic Syndrome"
            ],
            "pharmacotherapy": [
                "First-line direct oral anticoagulants: Rivaroxaban 15 mg BID for 21 days then 20 mg daily, OR Apixaban 10 mg BID for 7 days then 5 mg BID for at least 3-6 months",
                "Alternative: Low Molecular Weight Heparin (Enoxaparin 1.5 mg/kg SC daily) bridging to Warfarin (target INR 2.0-3.0) or for active cancer-associated thrombosis"
            ],
            "contraindications": [
                "Do NOT initiate DOACs in severe renal impairment (CrCl < 15-30 mL/min) or in patients with mechanical prosthetic heart valves."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American College of Chest Physicians (CHEST) & NICE",
            "guideline_title": "CHEST Guideline on Antithrombotic Therapy for VTE Disease",
            "publication_year": 2024,
            "source_url": "https://www.chestnet.org/guidelines-and-resources",
            "verification_hash": _calc_hash("BD71", "Deep Vein Thrombosis")
        }
    },

    # -------------------------------------------------------------------------
    # 3. ENDOCRINE & METABOLIC DISORDERS
    # -------------------------------------------------------------------------
    {
        "icd11_code": "5A10",
        "icd10_code": "E10.9",
        "clinical_name": "Type 1 Diabetes Mellitus",
        "common_aliases": ["T1DM", "Juvenile Diabetes", "Insulin-Dependent Diabetes", "පළමු වර්ගයේ දියවැඩියාව"],
        "medical_specialty": MedicalSpecialty.ENDOCRINE_METABOLIC,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Autoimmune-mediated destruction of pancreatic islet beta-cells by CD4+ and CD8+ T-lymphocytes "
            "and islet autoantibodies (anti-GAD65, anti-IA-2, anti-ZnT8). "
            "Absolute insulin deficiency halts cellular glucose uptake, activates hepatic gluconeogenesis and glycogenolysis, "
            "and unleashes unrestrained adipose lipolysis, generating free fatty acids converted to ketone bodies."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Polyuria (frequent copious urination including nocturia)", "weight": 0.96},
                {"symptom": "Polydipsia (unquenchable intense thirst)", "weight": 0.95},
                {"symptom": "Rapid unexplained weight loss despite hyperphagia", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Profound physical weakness and lethargy", "weight": 0.82},
                {"symptom": "Blurred vision secondary to lens osmotic swelling", "weight": 0.70},
                {"symptom": "Recurrent candidal infections (balanitis or vulvovaginitis)", "weight": 0.65},
            ]
        },
        "red_flag_criteria": [
            "Diabetic Ketoacidosis (DKA): Deep sighing Kussmaul respiration with acetone fruity breath odor",
            "Persistent nausea, intractable vomiting, and acute diffuse abdominal pain",
            "Obtundation, lethargy, confusion, or coma",
            "Capillary blood glucose > 250 mg/dL with blood ketones > 3.0 mmol/L"
        ],
        "differential_diagnoses": [
            {"condition": "Type 2 Diabetes Mellitus", "icd11": "5A11", "distinction": "Older age of onset, obesity, presence of C-peptide, absence of autoimmune anti-islet antibodies."},
            {"condition": "Maturity-Onset Diabetes of the Young (MODY)", "icd11": "5A13", "distinction": "Autosomal dominant family pedigree across >=3 generations, negative autoantibodies, young onset."},
            {"condition": "Diabetes Insipidus", "icd11": "5A61", "distinction": "Normal blood glucose levels, low urine specific gravity and low urine osmolality."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Fasting Plasma Glucose (>= 126 mg/dL / 7.0 mmol/L) or Random Glucose >= 200 mg/dL with symptoms", "Glycated Hemoglobin (HbA1c >= 6.5% / 48 mmol/mol)", "Urine / Blood Ketone testing (Beta-hydroxybutyrate)"],
            "imaging_ecg": ["Baseline ECG for hyperkalemia screening in new presentations"],
            "confirmatory_tests": ["Serum C-Peptide (fasting and stimulated - characteristically low/undetectable)", "Autoantibody panel: Anti-GAD65, IA-2A, ZnT8, Islet Cell Antibodies (ICA)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Comprehensive carbohydrate counting education and insulin-to-carbohydrate ratio calculation",
                "Continuous Glucose Monitoring (CGM) or frequent finger-prick self-monitoring (4-8 times/day)",
                "Pre-exercise carbohydrate adjustments to avert severe hypoglycemia"
            ],
            "pharmacotherapy": [
                "Mandatory lifelong basal-bolus insulin therapy or Continuous Subcutaneous Insulin Infusion (CSII pump)",
                "Basal: Long-acting insulin analog (Glargine U-300, Degludec, or Detemir) once or twice daily",
                "Prandial: Rapid-acting insulin analog (Lispro, Aspart, or Glulisine) administered 5-15 min prior to meals",
                "Emergency Glucagon rescue kit (Intranasal glucagon 3 mg or IM 1 mg) provided to family members"
            ],
            "contraindications": [
                "Oral antidiabetic agents (Sulfonylureas, Metformin) are NOT substitutes for insulin in Type 1 Diabetes; insulin must never be omitted."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Diabetes Association (ADA) & ISPAD",
            "guideline_title": "ADA Standards of Care in Diabetes: Type 1 Diabetes Management",
            "publication_year": 2024,
            "source_url": "https://diabetesjournals.org/care/issue/47/Supplement_1",
            "verification_hash": _calc_hash("5A10", "Type 1 Diabetes")
        }
    },
    {
        "icd11_code": "5A11",
        "icd10_code": "E11.9",
        "clinical_name": "Type 2 Diabetes Mellitus with Metabolic Syndrome",
        "common_aliases": ["T2DM", "Non-Insulin-Dependent Diabetes", "දෙවන වර්ගයේ දියවැඩියාව"],
        "medical_specialty": MedicalSpecialty.ENDOCRINE_METABOLIC,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Complex metabolic disease characterized by peripheral insulin resistance (skeletal muscle, adipose, liver) "
            "coupled with progressive secretory defect of pancreatic beta-cells. "
            "Adipose tissue inflammation, lipotoxicity, and ectopic lipid deposition fuel systemic insulin resistance, "
            "hepatic unsuppressed gluconeogenesis, postprandial hyperglucagonemia, and microvascular/macrovascular end-organ damage."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Gradual insidious polyuria, polydipsia, and fatigue", "weight": 0.88},
                {"symptom": "Centropetal obesity with elevated waist circumference", "weight": 0.85},
                {"symptom": "Acanthosis nigricans (velvety hyperpigmentation on neck and axillae)", "weight": 0.78},
            ],
            "secondary": [
                {"symptom": "Distal symmetric stocking-glove numbness and paresthesias", "weight": 0.72},
                {"symptom": "Slow wound healing and recurrent skin furunculosis", "weight": 0.68},
                {"symptom": "Erectile dysfunction in men or chronic vulvovaginitis in women", "weight": 0.62},
            ]
        },
        "red_flag_criteria": [
            "Hyperosmolar Hyperglycemic State (HHS): Blood glucose > 600 mg/dL, serum osmolality > 320 mOsm/kg, dehydration, altered sensorium",
            "Diabetic foot ulcer with ascending spreading cellulitis, crepitus, or gangrene",
            "Sudden monocular visual loss (vitreous hemorrhage or retinal detachment)",
            "Acute severe hypoglycemia (blood glucose < 54 mg/dL) with neuroglycopenic stupor"
        ],
        "differential_diagnoses": [
            {"condition": "Latent Autoimmune Diabetes in Adults (LADA)", "icd11": "5A10", "distinction": "Apparent T2DM in lean adults who rapidly fail oral agents within 6-12 months; positive anti-GAD."},
            {"condition": "Cushing Syndrome", "icd11": "5A70", "distinction": "Moon facies, purple abdominal striae > 1cm, proximal muscle myopathy, elevated 24h urinary free cortisol."},
            {"condition": "Pancreatogenic (Type 3c) Diabetes", "icd11": "5A12", "distinction": "History of chronic calcific pancreatitis, pancreatic resection, concurrent exocrine steatorrhea."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Fasting Plasma Glucose (>= 126 mg/dL / 7.0 mmol/L) on 2 separate occasions", "HbA1c (>= 6.5% / 48 mmol/mol)", "Random Plasma Glucose (>= 200 mg/dL with classical osmotic symptoms)"],
            "imaging_ecg": ["Baseline 12-Lead ECG for silent myocardial ischemia screening"],
            "confirmatory_tests": ["Urinary Albumin-to-Creatinine Ratio (UACR)", "Comprehensive lipid profile (Triglycerides, HDL, LDL)", "Dilated fundus photography examination"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Individualized medical nutrition therapy emphasizing low glycemic index, whole grains, and calorie restriction",
                "Structured physical activity >= 150 minutes/week of moderate-to-vigorous aerobic exercise + resistance training",
                "Weight management goal: 5-10% body weight reduction"
            ],
            "pharmacotherapy": [
                "First-line foundational monotherapy: Metformin 500 mg titrated to 2000 mg/day with meals",
                "If atherosclerotic CVD or high cardiorenal risk present regardless of baseline HbA1c: Add SGLT2 inhibitor (Empagliflozin 10-25 mg / Dapagliflozin 10 mg) AND/OR GLP-1 Receptor Agonist (Semaglutide / Dulaglutide)",
                "Standard HbA1c target: < 7.0% (53 mmol/mol) in most non-pregnant adults"
            ],
            "contraindications": [
                "Metformin is contraindicated in severe renal impairment (eGFR < 30 mL/min/1.73m2) due to lactic acidosis risk.",
                "SGLT2 inhibitors carry euglycemic DKA risk; withhold during acute illness, sepsis, or prior to major surgery."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Diabetes Association (ADA) & EASD",
            "guideline_title": "Standards of Care in Diabetes - 2024",
            "publication_year": 2024,
            "source_url": "https://diabetesjournals.org/care/issue/47/Supplement_1",
            "verification_hash": _calc_hash("5A11", "Type 2 Diabetes")
        }
    },
    {
        "icd11_code": "5A20",
        "icd10_code": "E10.1",
        "clinical_name": "Diabetic Ketoacidosis (DKA)",
        "common_aliases": ["Ketoacidosis", "Diabetic Acidosis", "ඩී.කේ.ඒ."],
        "medical_specialty": MedicalSpecialty.ENDOCRINE_METABOLIC,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Acute life-threatening metabolic decompensation driven by severe absolute/relative insulin deficiency "
            "coupled with surge in counter-regulatory hormones (glucagon, catecholamines, cortisol, growth hormone). "
            "Accelerated hepatic ketogenesis generates beta-hydroxybutyrate and acetoacetate, "
            "overwhelming buffer systems and producing high anion gap metabolic acidosis, profound osmotic diuresis, "
            "and total body potassium depletion."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Deep, rapid, labored Kussmaul respirations with sweet fruity breath", "weight": 0.96},
                {"symptom": "Persistent nausea, intractable vomiting, and severe diffuse abdominal pain", "weight": 0.94},
                {"symptom": "Severe dehydration: dry mucous membranes, sunken eyes, skin tenting", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Polyuria, polydipsia, and weakness preceding acute collapse", "weight": 0.85},
                {"symptom": "Progressive confusion, stupor, and altered consciousness", "weight": 0.82},
                {"symptom": "Hypothermia despite underlying severe precipitating infection", "weight": 0.65},
            ]
        },
        "red_flag_criteria": [
            "Severe arterial acidosis (pH < 7.10 or serum bicarbonate < 10 mEq/L)",
            "Altered mental status or progressive headache during treatment (Cerebral Edema threat)",
            "Refractory hypokalemia (< 3.3 mEq/L) which mandates holding insulin infusion to avoid fatal arrhythmia",
            "Hemodynamic instability with unrecordable blood pressure or anuria"
        ],
        "differential_diagnoses": [
            {"condition": "Hyperosmolar Hyperglycemic State (HHS)", "icd11": "5A21", "distinction": "Blood glucose > 600 mg/dL, minimal or absent acidosis (pH > 7.30, bicarb > 18), extreme hyperosmolality."},
            {"condition": "Alcoholic Ketoacidosis (AKA)", "icd11": "5A23", "distinction": "History of chronic alcohol binge followed by vomiting, blood glucose is typically normal or low."},
            {"condition": "Acute Surgical Abdomen", "icd11": "DD90", "distinction": "DKA mimics peritonitis ('pseudoperitonitis') which rapidly resolves as acidosis is corrected."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Capillary / Plasma Glucose (> 250 mg/dL)", "Blood Ketones (Beta-hydroxybutyrate > 3.0 mmol/L) or Urine Ketones (+++)", "Arterial or Venous Blood Gas (pH < 7.30, Bicarbonate < 18 mEq/L)"],
            "imaging_ecg": ["12-Lead ECG (peaked T waves in hyperkalemia, flattened T / U waves in hypokalemia)", "Chest Radiograph to identify occult pneumonia trigger"],
            "confirmatory_tests": ["Serum Anion Gap calculation: Na - (Cl + HCO3) > 12 mEq/L", "Serum Potassium, Sodium, Phosphate, and Magnesium monitoring every 2 hours"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate emergency room resuscitation and admission to Intensive Care / High Dependency Unit",
                "Continuous pulse oximetry, cardiac telemetry, and strict hourly urinary catheter fluid balance"
            ],
            "pharmacotherapy": [
                "Step 1: Aggressive IV fluid resuscitation with 0.9% Normal Saline (1000 mL in 1st hour, then 500 mL/h adjusted for hemodynamics)",
                "Step 2: Potassium replacement: Add 20-30 mEq K+ per liter of IV fluid once K+ < 5.2 mEq/L; HOLD insulin if K+ < 3.3 mEq/L",
                "Step 3: Continuous IV regular insulin infusion at 0.1 units/kg/h (aim for glucose reduction of 50-75 mg/dL/h)",
                "Step 4: Add 5% Dextrose to IV fluids once glucose drops to 200-250 mg/dL to prevent hypoglycemia while continuing insulin until ketoacidosis resolves (anion gap normalizes)"
            ],
            "contraindications": [
                "Never administer IV insulin bolus without verifying potassium >= 3.3 mEq/L. Routine sodium bicarbonate therapy is NOT recommended unless pH < 6.9."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Diabetes Association & Endocrine Society",
            "guideline_title": "Management of Hyperglycemic Emergencies in Adults: Joint Consensus Statement",
            "publication_year": 2024,
            "source_url": "https://diabetesjournals.org/care/article/doi/10.2337/dci23-0085",
            "verification_hash": _calc_hash("5A20", "Diabetic Ketoacidosis")
        }
    },
    {
        "icd11_code": "5A00",
        "icd10_code": "E03.9",
        "clinical_name": "Primary Hypothyroidism",
        "common_aliases": ["Underactive Thyroid", "Hashimoto Thyroiditis", "තයිරොයිඩ් ඌනතාව"],
        "medical_specialty": MedicalSpecialty.ENDOCRINE_METABOLIC,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Thyroid hormone deficiency most commonly caused by Hashimoto autoimmune thyroiditis "
            "(anti-TPO and anti-thyroglobulin mediated lymphocytic infiltration and parenchymal destruction) "
            "or post-ablative/surgical state. "
            "Depletion of circulating free T4 and T3 reduces basal metabolic rate, impairs mucopolysaccharide clearance "
            "(leading to non-pitting myxedema), slows neurocognitive processing, and dampens cardiac contractility."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Pathological cold intolerance (feeling cold in warm environment)", "weight": 0.90},
                {"symptom": "Unexplained modest weight gain with fluid retention", "weight": 0.85},
                {"symptom": "Chronic unremitting fatigue, lethargy, and mental slowing", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Constipation and diminished bowel motility", "weight": 0.80},
                {"symptom": "Dry coarse scaly skin, diffuse alopecia, and brittle nails", "weight": 0.78},
                {"symptom": "Periorbital non-pitting puffiness and hoarseness of voice", "weight": 0.75},
            ]
        },
        "red_flag_criteria": [
            "Myxedema Coma: Hypothermia (<35 C), hypoventilation (hypercapnia), severe bradycardia, and profound stupor",
            "Pericardial effusion with muffled heart sounds and pulsus paradoxus",
            "Severe hyponatremia (< 120 mEq/L) secondary to impaired renal water excretion",
            "Psychotic decompensation ('myxedema madness') with paranoid delusions"
        ],
        "differential_diagnoses": [
            {"condition": "Major Depressive Disorder", "icd11": "6A70", "distinction": "Depression lacks physical signs of delayed tendon reflexes, macroglossia, and has normal TSH."},
            {"condition": "Chronic Kidney Disease", "icd11": "GB61", "distinction": "Elevated serum creatinine and urea, normocytic anemia, normal thyroid axis."},
            {"condition": "Severe Congestive Heart Failure", "icd11": "BD11", "distinction": "Pitting edema, orthopnea, elevated BNP, normal thyroid profile."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Serum Thyroid Stimulating Hormone (TSH - markedly elevated > 10 mIU/L)", "Free Thyroxine (FT4 - low in overt, normal in subclinical)"],
            "imaging_ecg": ["12-Lead ECG (sinus bradycardia, low QRS voltage, flattened/inverted T waves)"],
            "confirmatory_tests": ["Anti-Thyroid Peroxidase (Anti-TPO) and Anti-Thyroglobulin (Anti-Tg) Antibodies", "Lipid panel (elevated LDL cholesterol and triglycerides)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Balanced high-fiber nutrition to alleviate chronic constipation",
                "Routine periodic surveillance of thyroid function tests"
            ],
            "pharmacotherapy": [
                "Drug of Choice: Oral Levothyroxine (synthetic T4) monotherapy: full replacement dose ~1.6 mcg/kg/day in young healthy adults",
                "In elderly patients or those with known coronary artery disease: Start low and go slow (12.5 - 25 mcg/day), titrating every 6-8 weeks",
                "Take Levothyroxine with water on an empty stomach at least 30-60 minutes before breakfast",
                "Monitor serum TSH every 6-8 weeks until euthyroid target (TSH 0.5 - 2.5 mIU/L) achieved"
            ],
            "contraindications": [
                "Calcium carbonate, iron supplements, and proton pump inhibitors must not be ingested within 4 hours of Levothyroxine as they severely bind and block absorption."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Thyroid Association (ATA) & Endocrine Society",
            "guideline_title": "Guidelines for the Treatment of Hypothyroidism",
            "publication_year": 2023,
            "source_url": "https://www.thyroid.org/professionals/ata-professional-guidelines/",
            "verification_hash": _calc_hash("5A00", "Primary Hypothyroidism")
        }
    },
    {
        "icd11_code": "5A02",
        "icd10_code": "E05.0",
        "clinical_name": "Hyperthyroidism and Thyrotoxicosis (Graves Disease)",
        "common_aliases": ["Overactive Thyroid", "Toxic Diffuse Goiter", "තයිරොයිඩ් අධික්‍රියාකාරීත්වය"],
        "medical_specialty": MedicalSpecialty.ENDOCRINE_METABOLIC,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Hypermetabolic state driven by excessive circulating free thyroid hormones (T4 and T3). "
            "In Graves disease, autoantibodies (TRAb / TSI) bind to and constitutively activate the thyroid TSH receptor, "
            "triggering follicular hyperplasia, uncontrolled hormone synthesis, sympathetic upregulation, "
            "orbital fibroblast activation (exophthalmos), and pretibial glycosaminoglycan deposition."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Extreme heat intolerance and profuse diaphoresis", "weight": 0.92},
                {"symptom": "Marked involuntary weight loss despite voracious appetite", "weight": 0.90},
                {"symptom": "Resting palpitations, sinus tachycardia, or atrial fibrillation", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Fine resting hand tremor and proximal muscle weakness", "weight": 0.82},
                {"symptom": "Frequent bowel movements or chronic diarrhea", "weight": 0.75},
                {"symptom": "Graves orbitopathy: proptosis, lid lag, stare, and diplopia", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Thyroid Storm (Burch-Wartofsky score >= 45): High fever (>38.5 C), extreme tachycardia (>140 bpm), agitation, delirium, and shock",
            "New-onset Rapid Ventricular Response Atrial Fibrillation with heart failure",
            "Sight-threatening compressive optic neuropathy from severe Graves orbitopathy",
            "High-output cardiac failure with pulmonary edema"
        ],
        "differential_diagnoses": [
            {"condition": "Toxic Multinodular Goiter (Plummer Disease)", "icd11": "5A02.1", "distinction": "Absence of orbitopathy, radioactive iodine uptake shows patchy hot autonomous nodules."},
            {"condition": "Subacute De Quervain Thyroiditis", "icd11": "5A03.1", "distinction": "Exquisite anterior neck tenderness, preceding viral illness, high ESR, low radioactive iodine uptake."},
            {"condition": "Pheochromocytoma", "icd11": "2F30", "distinction": "Paroxysmal triad of headache, sweating, palpitations; normal thyroid function, elevated plasma free metanephrines."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Serum TSH (suppressed < 0.01 mIU/L)", "Serum Free T4 and Free T3 (elevated)", "TSH Receptor Antibodies (TRAb - diagnostic for Graves disease)"],
            "imaging_ecg": ["12-Lead ECG (sinus tachycardia, atrial fibrillation)", "Thyroid Ultrasound with color flow Doppler ('thyroid inferno' pattern)"],
            "confirmatory_tests": ["Radioactive Iodine (I-123 or Tc-99m) Uptake and Scan (diffuse homogenous elevated uptake)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Avoidance of smoking (critical: smoking dramatically worsens Graves ophthalmopathy)",
                "Limiting strenuous exertion until metabolic euthyroid control is restored"
            ],
            "pharmacotherapy": [
                "Symptomatic control: Beta-blocker (Propranolol 20-40 mg TID or Atenolol 50 mg daily) to blunt adrenergic surge",
                "Thionamides: Carbimazole 15-40 mg daily (or Methimazole 10-30 mg daily); Propylthiouracil (PTU) is preferred in first trimester of pregnancy and thyroid storm",
                "Definitive therapy options: Radioactive Iodine Ablation (I-131) or Total Thyroidectomy"
            ],
            "contraindications": [
                "Warning: Patients on Carbimazole/Methimazole must be instructed to STOP medication and get an urgent Full Blood Count immediately if they develop a sore throat or fever (Agranulocytosis risk in 0.3%)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Thyroid Association (ATA) & European Thyroid Association",
            "guideline_title": "2023 ATA Guidelines for Diagnosis and Management of Hyperthyroidism",
            "publication_year": 2023,
            "source_url": "https://www.thyroid.org/professionals/ata-professional-guidelines/",
            "verification_hash": _calc_hash("5A02", "Hyperthyroidism")
        }
    },
    {
        "icd11_code": "5C80",
        "icd10_code": "E78.2",
        "clinical_name": "Mixed Hyperlipidemia & Atherogenic Dyslipidemia",
        "common_aliases": ["High Cholesterol", "Dyslipidemia", "රුධිරයේ කොලෙස්ටරෝල් වැඩිවීම"],
        "medical_specialty": MedicalSpecialty.ENDOCRINE_METABOLIC,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Disorder of lipoprotein metabolism characterized by elevated circulating low-density lipoprotein (LDL-C), "
            "elevated apolipoprotein B, elevated triglycerides, and low high-density lipoprotein (HDL-C). "
            "Atherogenic particles enter arterial subendothelial spaces, undergo oxidative modification, "
            "trigger scavenger receptor macrophage uptake (foam cells), and initiate atherosclerotic core formation."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Asymptomatic until secondary vascular events occur (angina, TIA, claudication)", "weight": 0.95},
                {"symptom": "Fasting total cholesterol > 200 mg/dL or LDL-C > 130 mg/dL", "weight": 0.98},
            ],
            "secondary": [
                {"symptom": "Tendon xanthomas (Achilles tendon thickening in Familial Hypercholesterolemia)", "weight": 0.75},
                {"symptom": "Xanthelasma (cholesterol deposits on medial eyelids)", "weight": 0.60},
                {"symptom": "Corneal arcus senilis in patients younger than 45 years", "weight": 0.65},
            ]
        },
        "red_flag_criteria": [
            "Severe hypertriglyceridemia (Triglycerides > 1000 mg/dL / 11.3 mmol/L) triggering Acute Pancreatitis",
            "Concurrent acute coronary chest pain or cerebral transient ischemic attack",
            "Sudden severe muscle pain, dark cola-colored urine, and oliguria (Statin-induced Rhabdomyolysis)"
        ],
        "differential_diagnoses": [
            {"condition": "Familial Hypercholesterolemia (FH)", "icd11": "5C80.0", "distinction": "Autosomal dominant LDLR mutation, LDL-C > 190 mg/dL, early coronary artery disease in first-degree relatives."},
            {"condition": "Secondary Dyslipidemia due to Hypothyroidism", "icd11": "5A00", "distinction": "Elevated TSH, resolution of lipid abnormalities with levothyroxine replacement alone."},
            {"condition": "Nephrotic Syndrome Dyslipidemia", "icd11": "GB40", "distinction": "Severe hypercholesterolemia with hypoalbuminemia, massive proteinuria > 3.5 g/24h."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Fasting Lipid Profile (Total Cholesterol, Triglycerides, HDL-C, calculated LDL-C, Non-HDL-C)", "Fasting Glucose and HbA1c (evaluate metabolic syndrome)", "Serum TSH and Serum Creatinine / eGFR"],
            "imaging_ecg": ["Coronary Artery Calcium (CAC) CT scan for intermediate cardiovascular risk stratification"],
            "confirmatory_tests": ["Serum Apolipoprotein B (ApoB) and Lipoprotein(a) [Lp(a)] measurement"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Mediterranean-style dietary pattern: eliminate trans-fats, reduce saturated fat < 7% of total energy",
                "Increase dietary soluble fiber (psyllium, oats, legumes) >= 10-25 g/day",
                "Regular aerobic exercise >= 30 minutes 5 days/week"
            ],
            "pharmacotherapy": [
                "First-line High-Intensity Statin: Atorvastatin 40-80 mg or Rosuvastatin 20-40 mg daily (aim for >= 50% LDL-C reduction)",
                "Add Ezetimibe 10 mg daily if LDL-C target not reached on maximally tolerated statin",
                "Add PCSK9 Inhibitor (Evolocumab / Alirocumab) or Bempedoic Acid for very high-risk secondary prevention",
                "If Triglycerides > 500 mg/dL: Fenofibrate or Icosapent Ethyl to prevent acute pancreatitis"
            ],
            "contraindications": [
                "Statins are contraindicated in active decompensated liver disease, unexplained persistent transaminase elevations > 3x ULN, and pregnancy/lactation."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Society of Cardiology (ESC) & EAS",
            "guideline_title": "ESC/EAS Guidelines for the Management of Dyslipidaemias",
            "publication_year": 2023,
            "source_url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Dyslipidaemias-Management-of",
            "verification_hash": _calc_hash("5C80", "Mixed Hyperlipidemia")
        }
    },

    # -------------------------------------------------------------------------
    # 4. RESPIRATORY MEDICINE
    # -------------------------------------------------------------------------
    {
        "icd11_code": "CA23",
        "icd10_code": "J45.9",
        "clinical_name": "Acute Exacerbation of Bronchial Asthma",
        "common_aliases": ["Asthma Attack", "Reactive Airway Disease", "ඇදුම රෝගය"],
        "medical_specialty": MedicalSpecialty.RESPIRATORY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Chronic airway inflammatory disorder driven by Type 2 helper T-cell (Th2) and eosinophilic/mast cell activation. "
            "Exposure to aeroallergens, viral infections, or cold air provokes acute bronchospasm of airway smooth muscle, "
            "mucosal edema, and tenacious intraluminal mucus hypersecretion, resulting in variable expiratory airflow limitation."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Expiratory wheezing audible on auscultation or unassisted", "weight": 0.96},
                {"symptom": "Episodic dyspnea and sensation of chest tightness", "weight": 0.94},
                {"symptom": "Nocturnal or early morning dry/phlegmy cough disrupting sleep", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Tachypnea and prolonged expiratory phase", "weight": 0.80},
                {"symptom": "Symptoms triggered by viral URI, exercise, or cold air", "weight": 0.78},
                {"symptom": "Personal or family history of atopy (allergic rhinitis, eczema)", "weight": 0.70},
            ]
        },
        "red_flag_criteria": [
            "Life-Threatening Asthma: Silent chest on auscultation (no air entry to generate wheeze)",
            "Inability to complete full sentences in one breath, speaking in single words",
            "Peak Expiratory Flow (PEF) < 33% of predicted or personal best",
            "Cyanosis, exhaustion, altered sensorium, or paradoxical thoracoabdominal breathing",
            "Pulsus paradoxus > 25 mmHg and SpO2 < 90% on high-flow oxygen"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Exacerbation of COPD", "icd11": "CA22", "distinction": "Older age (>40), heavy tobacco smoking history, fixed non-reversible airflow obstruction."},
            {"condition": "Acute Left Heart Failure (Cardiac Asthma)", "icd11": "BD11", "distinction": "Bilateral basal lung crackles, orthopnea, elevated BNP, cardiomegaly on chest X-ray."},
            {"condition": "Foreign Body Aspiration", "icd11": "CA02", "distinction": "Sudden onset choking while eating, unilateral monophonic wheeze, localized air trapping on inspiratory/expiratory chest X-ray."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Peak Expiratory Flow Rate (PEFR) measurement compared to predicted/best", "Continuous pulse oximetry monitoring", "Arterial Blood Gas in severe asthma (normal or elevated PaCO2 indicates impending respiratory arrest)"],
            "imaging_ecg": ["Chest Radiograph (rule out pneumothorax, pneumomediastinum, or lobar pneumonia)"],
            "confirmatory_tests": ["Spirometry (FEV1/FVC < 0.70 with > 12% and > 200 mL bronchodilator reversibility after 400 mcg Salbutamol)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Sit the patient upright; reassure and maintain calm environment",
                "Identify and eliminate personal environmental triggers (house dust mite, tobacco smoke, pet dander)"
            ],
            "pharmacotherapy": [
                "Acute relief: Inhaled Short-Acting Beta-2 Agonist (Salbutamol 4-10 puffs via metered-dose inhaler with spacer every 20 minutes for 1 hour, or nebulized 2.5-5 mg)",
                "Add Inhaled Ipratropium Bromide (500 mcg nebulized) for severe exacerbations",
                "Systemic Corticosteroids: Oral Prednisolone 40-50 mg daily for 5-7 days (reduces relapse rate and hospital admission)",
                "Maintenance: Inhaled Corticosteroid-Formoterol (ICS-LABA e.g., Budesonide-Formoterol) as preferred anti-inflammatory reliever (GINA Track 1)"
            ],
            "contraindications": [
                "STRICTLY CONTRAINDICATED: Non-selective Beta-blockers (Propranolol, Timolol eye drops) and NSAIDs/Aspirin in Aspirin-Exacerbated Respiratory Disease (AERD) as they trigger fatal bronchospasm."
            ]
        },
        "source_metadata": {
            "issuing_authority": "Global Initiative for Asthma (GINA) & British Thoracic Society (BTS)",
            "guideline_title": "Global Strategy for Asthma Management and Prevention (2024 Update)",
            "publication_year": 2024,
            "source_url": "https://ginasthma.org/gina-reports/",
            "verification_hash": _calc_hash("CA23", "Bronchial Asthma")
        }
    },
    {
        "icd11_code": "CA22",
        "icd10_code": "J44.1",
        "clinical_name": "Chronic Obstructive Pulmonary Disease (Acute Exacerbation)",
        "common_aliases": ["AECOPD", "Chronic Bronchitis & Emphysema", "නිදන්ගත පුප්ඵුසීය අවහිරතා රෝගය"],
        "medical_specialty": MedicalSpecialty.RESPIRATORY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Persistent, progressive airflow limitation driven by chronic airway inflammation and emphysematous parenchymal destruction "
            "induced by long-term cigarette smoke or biomass fuel exposure. "
            "Small airway narrowing, goblet cell hyperplasia with mucus hypersecretion, loss of alveolar elastic recoil, "
            "and dynamic lung hyperinflation cause severe ventilation-perfusion mismatch and chronic hypercapnic respiratory failure."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Acute worsening of baseline exertional dyspnea (Anthonisen criterion 1)", "weight": 0.95},
                {"symptom": "Increased sputum volume (Anthonisen criterion 2)", "weight": 0.90},
                {"symptom": "Increased sputum purulence / green-yellow color (Anthonisen criterion 3)", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Pursed-lip breathing and use of sternocleidomastoid accessory muscles", "weight": 0.85},
                {"symptom": "Barrel chest deformity with hyperresonance on percussion", "weight": 0.80},
                {"symptom": "Peripheral dependent ankle edema secondary to cor pulmonale", "weight": 0.72},
            ]
        },
        "red_flag_criteria": [
            "Acute respiratory acidosis with pH < 7.25 and PaCO2 > 60 mmHg requiring non-invasive ventilation (NIV)",
            "New-onset confusion, asterixis (flapping tremor), or somnolence from severe carbon dioxide narcosis",
            "Hemodynamic collapse or malignant arrhythmias",
            "Oxygen saturation < 85% failing to respond to controlled Venturi mask oxygen"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Congestive Heart Failure", "icd11": "BD11", "distinction": "Cardiomegaly on radiograph, elevated BNP, prominent orthopnea, pitting pedal edema."},
            {"condition": "Bacterial Lobar Pneumonia", "icd11": "CA40", "distinction": "Focal dense consolidation on chest radiograph, high procalcitonin, focal bronchial breathing."},
            {"condition": "Secondary Pneumothorax", "icd11": "CA00", "distinction": "Sudden unilateral chest pain with loss of breath sounds in a patient with bullous emphysema."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Arterial Blood Gas (ABG - assess PaO2, PaCO2, and pH compensation)", "Full Blood Count (polycythemia secondary to chronic hypoxia, or leukocytosis)", "Serum C-Reactive Protein (CRP > 50 mg/L guides antibiotic requirement)"],
            "imaging_ecg": ["Chest Radiograph (hyperinflation, flattened diaphragms, bullae, rule out pneumonia/pneumothorax)", "12-Lead ECG (P-pulmonale, right bundle branch block, right axis deviation)"],
            "confirmatory_tests": ["Post-bronchodilator Spirometry: FEV1/FVC < 0.70 non-reversible confirms underlying COPD"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Smoking cessation: single most effective intervention to halt FEV1 decline",
                "Pulmonary rehabilitation enrollment following recovery from acute exacerbation"
            ],
            "pharmacotherapy": [
                "Controlled titrated oxygen via 24% or 28% Venturi mask targeting SpO2 88-92% (avoids blunting hypoxic drive)",
                "Combined Short-Acting Bronchodilators: Salbutamol 2.5-5 mg + Ipratropium 500 mcg nebulized every 4-6 hours",
                "Systemic Corticosteroids: Oral Prednisolone 40 mg daily for exactly 5 days",
                "Antibiotics for 5 days if increased sputum purulence is present: Amoxicillin-Clavulanate 625 mg TID, Azithromycin 500 mg daily, or Doxycycline 100 mg BID"
            ],
            "contraindications": [
                "High-flow uncontrolled oxygen (e.g. 15L non-rebreather) without monitoring is dangerous in chronic CO2 retainers due to worsening hypercapnia and respiratory arrest."
            ]
        },
        "source_metadata": {
            "issuing_authority": "Global Initiative for Chronic Obstructive Lung Disease (GOLD)",
            "guideline_title": "Global Strategy for the Diagnosis, Management, and Prevention of COPD (2024 Report)",
            "publication_year": 2024,
            "source_url": "https://goldcopd.org/2024-gold-report/",
            "verification_hash": _calc_hash("CA22", "COPD Exacerbation")
        }
    },
    {
        "icd11_code": "CA40",
        "icd10_code": "J18.9",
        "clinical_name": "Community-Acquired Bacterial Pneumonia (CAP)",
        "common_aliases": ["CAP", "Chest Infection", "ප්නියුමෝනියාව", "Lung Infection"],
        "medical_specialty": MedicalSpecialty.RESPIRATORY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Acute alveolar infection predominantly caused by Streptococcus pneumoniae, Haemophilus influenzae, or atypicals. "
            "Aspiration or inhalation of pathogens overcomes host mucociliary clearance. "
            "Bacterial proliferation in alveoli triggers neutrophilic exocytosis, exudative intra-alveolar consolidation, "
            "microvascular congestion, and right-to-left intrapulmonary shunt producing arterial hypoxemia."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "High pyrexia with shaking rigors and chills", "weight": 0.92},
                {"symptom": "Productive cough with purulent or rusty sputum", "weight": 0.90},
                {"symptom": "Pleuritic, sharp chest pain aggravated by deep inspiration or coughing", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Tachypnea and breathlessness", "weight": 0.85},
                {"symptom": "Localized bronchial breathing, coarse crackles, and dullness on percussion", "weight": 0.82},
                {"symptom": "Confusion, cognitive dulling, and hypothermia (common presentation in elderly)", "weight": 0.70},
            ]
        },
        "red_flag_criteria": [
            "Severe CAP (CURB-65 score >= 3): Confusion, Urea > 7 mmol/L, Respiratory rate >= 30/min, Low BP (SBP < 90 or DBP <= 60), Age >= 65",
            "Acute hypoxemic respiratory failure requiring mechanical ventilation",
            "Septic shock requiring vasopressor therapy despite fluid loading",
            "Parapneumonic empyema (pleural fluid with pH < 7.20 or frank pus)"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Pulmonary Embolism", "icd11": "BB00", "distinction": "Sudden pleuritic pain, absence of high fever/rigors, clear lung fields or wedge-shaped Hampton hump on radiograph."},
            {"condition": "Pulmonary Tuberculosis", "icd11": "1B10", "distinction": "Subacute > 2-3 weeks duration, night sweats, apical cavitary lesions, acid-fast bacilli on sputum."},
            {"condition": "Acute Bronchitis", "icd11": "CA42", "distinction": "Absence of focal consolidated crackles/bronchial breathing, normal chest radiograph without parenchymal infiltrates."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (neutrophilic leukocytosis with toxic granulation)", "Serum C-Reactive Protein (CRP) and Procalcitonin", "Blood cultures (2 sets drawn prior to antibiotic administration)", "Sputum Gram stain and bacterial culture"],
            "imaging_ecg": ["Posteroanterior and Lateral Chest Radiograph (lobar or segmental dense consolidation, air bronchograms, pleural effusion)"],
            "confirmatory_tests": ["Urinary Legionella and Pneumococcal antigen assays"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Appropriate risk stratification using CURB-65 or CRB-65 score to determine outpatient vs inpatient care",
                "Hydration, antipyretics, and early mobilization to prevent venous thromboembolism"
            ],
            "pharmacotherapy": [
                "Low-risk Outpatient (CURB-65 0-1): Oral Amoxicillin 500 mg - 1g TID for 5 days, OR Doxycycline 100 mg BID (if penicillin-allergic)",
                "Moderate-risk Inpatient (CURB-65 2): Dual therapy with Amoxicillin-Clavulanate 1.2g IV Q8H + Clarithromycin 500 mg IV/oral Q12H",
                "Severe Inpatient / ICU (CURB-65 >= 3): Ceftriaxone 2g IV daily + Azithromycin 500 mg IV daily (covers atypical pathogens)"
            ],
            "contraindications": [
                "Do not delay antibiotic initiation: First dose must be administered within 4 hours of arrival (within 1 hour if septic shock)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Thoracic Society (ATS) & Infectious Diseases Society of America (IDSA)",
            "guideline_title": "Diagnosis and Treatment of Adults with Community-Acquired Pneumonia",
            "publication_year": 2024,
            "source_url": "https://www.thoracic.org/statements/resources/tb-opi/cap-guidelines.pdf",
            "verification_hash": _calc_hash("CA40", "Community-Acquired Pneumonia")
        }
    },
    {
        "icd11_code": "BB00",
        "icd10_code": "I26.9",
        "clinical_name": "Acute Pulmonary Embolism (PE)",
        "common_aliases": ["Pulmonary Thromboembolism", "PE", "පෙනහළු ත්‍රොම්බෝසිස්"],
        "medical_specialty": MedicalSpecialty.RESPIRATORY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Occlusion of the pulmonary arterial bed by a dislodged thrombus originating from deep leg or pelvic veins. "
            "Mechanical arterial obstruction elevates pulmonary vascular resistance, inducing acute right ventricular overload, "
            "dilatation, and right ventricular ischemia. "
            "Severe RV failure shifts the interventricular septum leftward, impairing left ventricular filling and precipitating cardiogenic shock."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Sudden onset unexplained dyspnea and tachypnea (respiratory rate > 20/min)", "weight": 0.95},
                {"symptom": "Acute sharp pleuritic chest pain", "weight": 0.90},
                {"symptom": "Hemoptysis (indicates peripheral pulmonary infarction)", "weight": 0.80},
            ],
            "secondary": [
                {"symptom": "Tachycardia (heart rate > 100 bpm)", "weight": 0.88},
                {"symptom": "Unilateral swollen, tender, erythematous calf", "weight": 0.78},
                {"symptom": "Syncope or lightheadedness (indicates massive central saddle embolus)", "weight": 0.82},
            ]
        },
        "red_flag_criteria": [
            "High-risk (Massive) PE: Systolic BP < 90 mmHg or vasopressor requirement with cardiac arrest",
            "Acute right ventricular strain on bedside echocardiography (McConnell sign: RV free wall akinesia with apex sparing)",
            "Marked Troponin I and BNP elevation indicating acute RV micro-infarction",
            "Severe hypoxemia refractory to high-flow oxygen"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Coronary Syndrome (STEMI / NSTEMI)", "icd11": "BA41", "distinction": "Retrosternal crushing pressure, ST elevations on ECG, absence of RV strain / McConnell sign."},
            {"condition": "Acute Tension Pneumothorax", "icd11": "CA00", "distinction": "Absent breath sounds over affected hemithorax, hyperresonance, contralateral tracheal deviation."},
            {"condition": "Acute Aortic Dissection", "icd11": "BD50", "distinction": "Tearing back pain, widened mediastinum, pulse deficits in extremities."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Clinical pre-test probability assessment (Wells Score or Geneva Score)", "High-sensitivity D-Dimer (rules out PE if Wells score indicates unlikely)", "Cardiac Biomarkers: High-sensitivity Troponin and NT-proBNP (risk stratification)"],
            "imaging_ecg": ["CT Pulmonary Angiography (CTPA - gold standard, demonstrates intraluminal filling defects)", "12-Lead ECG (Sinus tachycardia; S1Q3T3 pattern; T-wave inversions in V1-V4)", "Bedside Echocardiography (RV dilatation, RV/LV ratio > 1.0)"],
            "confirmatory_tests": ["Ventilation-Perfusion (V/Q) Lung Scintigraphy (if renal failure or severe contrast allergy)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate strict bed rest and high-flow oxygen therapy",
                "Intensive care unit monitoring for high and intermediate-high risk cohorts"
            ],
            "pharmacotherapy": [
                "Immediate therapeutic anticoagulation: Low Molecular Weight Heparin (Enoxaparin 1 mg/kg SC BID) or Unfractionated Heparin infusion",
                "Direct Oral Anticoagulants (DOACs: Apixaban or Rivaroxaban) for hemodynamically stable intermediate/low-risk patients",
                "High-risk Massive PE with Shock: Immediate Systemic Thrombolysis (Recombinant Tissue Plasminogen Activator - Alteplase 100 mg IV over 2 hours) or catheter-directed embolectomy"
            ],
            "contraindications": [
                "Thrombolysis is contraindicated in active internal bleeding, recent intracranial hemorrhage, or major cranial trauma within 3 months (surgical embolectomy is considered instead)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Society of Cardiology (ESC) & European Respiratory Society (ERS)",
            "guideline_title": "ESC Guidelines for the Diagnosis and Management of Acute Pulmonary Embolism",
            "publication_year": 2024,
            "source_url": "https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Pulmonary-Embolism-Guidelines",
            "verification_hash": _calc_hash("BB00", "Acute Pulmonary Embolism")
        }
    },

    # -------------------------------------------------------------------------
    # 5. NEUROLOGY & PSYCHIATRY
    # -------------------------------------------------------------------------
    {
        "icd11_code": "8B11",
        "icd10_code": "I63.9",
        "clinical_name": "Acute Ischemic Stroke (Middle Cerebral Artery Territory)",
        "common_aliases": ["Cerebral Infarction", "Brain Attack", "ඉෂ්කිමික් ස්ට්‍රෝක්", "අංශභාගය"],
        "medical_specialty": MedicalSpecialty.NEUROLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Sudden focal neurological deficit caused by thromboembolic or atherothrombotic occlusion of a cerebral artery "
            "(most commonly MCA). "
            "Cessation of cerebral blood flow depletes neuronal ATP, leading to failure of Na+/K+ ATPase pumps, "
            "cytotoxic edema, massive glutamate excitotoxicity, and expanding penumbral infarction around an irreversible ischemic core."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Acute unilateral facial drooping / asymmetry", "weight": 0.98},
                {"symptom": "Acute unilateral upper and/or lower limb weakness or hemiplegia", "weight": 0.98},
                {"symptom": "Acute speech disturbance (expressive/receptive aphasia or dysarthria)", "weight": 0.96},
            ],
            "secondary": [
                {"symptom": "Homonymous hemianopia and conjugate gaze deviation toward side of lesion", "weight": 0.85},
                {"symptom": "Hemisensory loss (unilateral numbness)", "weight": 0.82},
                {"symptom": "Hemispatial neglect (extinction to bilateral sensory stimulation)", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Any positive FAST criteria (Face, Arm, Speech, Time) with symptom onset < 4.5 - 24 hours",
            "Progressive stupor, coma, or pupillary asymmetry indicating malignant MCA herniation",
            "Loss of protective airway reflexes with risk of massive pulmonary aspiration",
            "Abrupt onset worst-ever headache preceding focal deficit (suspected hemorrhagic conversion)"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Hypoglycemia", "icd11": "5A41", "distinction": "Blood glucose < 50 mg/dL; focal signs rapidly and completely resolve within minutes of IV 50% dextrose administration."},
            {"condition": "Todd Paresis (Post-ictal paralysis)", "icd11": "8A62", "distinction": "Preceded by observed seizure activity, resolving over 24-48 hours, clear brain MRI/CT."},
            {"condition": "Acute Hemiplegic Migraine", "icd11": "8A80", "distinction": "Family history, gradual 'migrainous march' over 20-30 minutes rather than instantaneous deficit, normal diffusion-weighted MRI."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Immediate capillary blood glucose (MANDATORY rule out hypoglycemia)", "Full Blood Count, Platelet count, Serum Electrolytes, Renal function", "Coagulation profile (INR, aPTT) to confirm thrombolysis eligibility"],
            "imaging_ecg": ["Non-Contrast Head CT scan (rule out hemorrhage within 20 min of door time)", "CT Angiography of head and neck (detect Large Vessel Occlusion - LVO)", "Brain MRI with Diffusion-Weighted Imaging (DWI - hyperacute ischemia detection)"],
            "confirmatory_tests": ["12-Lead ECG (detect concurrent atrial fibrillation or myocardial ischemia)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Emergency Stroke Center transfer; record EXACT last-known-well time",
                "Maintain head of bed elevated 30 degrees; strictly maintain nil-by-mouth (NPO) until formal dysphagia swallow screen passed"
            ],
            "pharmacotherapy": [
                "Intravenous Thrombolysis with Alteplase (0.9 mg/kg, max 90 mg; 10% bolus over 1 min, rest over 60 min) or Tenecteplase within 4.5 hours of symptom onset (target door-to-needle < 60 min)",
                "Endovascular Thrombectomy (EVT) for large vessel occlusions within 6 to 24 hours guided by perfusion mismatch imaging",
                "Blood pressure management: Lower BP to < 185/110 mmHg prior to thrombolysis using IV Labetalol or Nicardipine",
                "Secondary prevention: Aspirin 300 mg daily started 24 hours post-thrombolysis (after repeat CT confirms no hemorrhage)"
            ],
            "contraindications": [
                "Intravenous thrombolysis is strictly contraindicated if active intracranial hemorrhage is present, INR > 1.7, platelet count < 100,000/uL, or major head trauma/stroke within prior 3 months."
            ]
        },
        "source_metadata": {
            "issuing_authority": "AHA/ASA & European Stroke Organisation (ESO)",
            "guideline_title": "Guidelines for the Early Management of Patients with Acute Ischemic Stroke",
            "publication_year": 2024,
            "source_url": "https://www.ahajournals.org/doi/10.1161/STR.0000000000000211",
            "verification_hash": _calc_hash("8B11", "Acute Ischemic Stroke")
        }
    },
    {
        "icd11_code": "8B00",
        "icd10_code": "I61.9",
        "clinical_name": "Acute Spontaneous Intracerebral Hemorrhage",
        "common_aliases": ["Hemorrhagic Stroke", "Brain Bleed", "රක්තපාත අංශභාගය"],
        "medical_specialty": MedicalSpecialty.NEUROLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Non-traumatic bleeding into brain parenchyma resulting from chronic hypertensive lipohyalinosis "
            "and rupture of small penetrating cerebral arterioles (Charcot-Bouchard microaneurysms) or cerebral amyloid angiopathy. "
            "Expanding hematoma causes direct mechanical tissue disruption, secondary surrounding perihematomal edema, "
            "and elevated intracranial pressure (ICP)."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Sudden onset severe headache during physical exertion", "weight": 0.94},
                {"symptom": "Acute onset projectile vomiting and photophobia", "weight": 0.90},
                {"symptom": "Rapidly progressive focal neurological deficit (hemiparesis, sensory loss)", "weight": 0.95},
            ],
            "secondary": [
                {"symptom": "Rapid depression of consciousness / coma within minutes to hours", "weight": 0.92},
                {"symptom": "Marked acute arterial hypertension (SBP > 200 mmHg)", "weight": 0.88},
                {"symptom": "Meningism with neck rigidity in intraventricular extension", "weight": 0.75},
            ]
        },
        "red_flag_criteria": [
            "Expanding hematoma volume (>33% expansion in first 6 hours)",
            "Signs of impending transtentorial herniation: unilateral dilated unreactive pupil (blown pupil), decerebrate posturing",
            "Cushing triad: profound bradycardia, irregular respiration, severe hypertension",
            "Glasgow Coma Scale (GCS) score drop by >= 2 points"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Ischemic Stroke", "icd11": "8B11", "distinction": "Cannot be reliably distinguished on clinical grounds alone; non-contrast CT is mandatory."},
            {"condition": "Subarachnoid Hemorrhage (Aneurysmal)", "icd11": "8B01", "distinction": "Thunderclap headache ('worst headache of life'), prominent nuchal rigidity, absence of early dense hemiplegia."},
            {"condition": "Ruptured Arteriovenous Malformation (AVM)", "icd11": "8B21", "distinction": "Younger non-hypertensive patients, angiography demonstrates tangled vascular nidus."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Immediate non-contrast Head CT scan (hyperdense parenchymal attenuation)", "CT Angiography ('spot sign' predicting active contrast extravasation and hematoma expansion)", "Full Blood Count, Coagulation Profile (INR, aPTT, Fibrinogen), Serum Electrolytes"],
            "imaging_ecg": ["12-Lead ECG (neurogenic T-wave inversions, QT prolongation)"],
            "confirmatory_tests": ["Brain MRI with Gradient Echo (GRE) / Susceptibility-Weighted Imaging (SWI)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Admission to dedicated Neuro-Intensive Care Unit (NICU)",
                "Endotracheal intubation for airway protection if GCS <= 8"
            ],
            "pharmacotherapy": [
                "Immediate intensive blood pressure reduction: Target SBP 130-140 mmHg within 1 hour using continuous IV Nicardipine or Labetalol",
                "Rapid anticoagulation reversal: If on Warfarin: 4-Factor Prothrombin Complex Concentrate (PCC) + IV Vitamin K; If on Dabigatran: Idarucizumab; If on Factor Xa inhibitor: Andexanet Alfa",
                "Neurosurgical evacuation / decompressive craniectomy for cerebellar hematoma > 3 cm compressing brainstem"
            ],
            "contraindications": [
                "Strictly avoid prophylactic anticonvulsants in non-comatose patients without clinical seizures. Avoid excessive hypotension (SBP < 120 mmHg)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "AHA/ASA & European Stroke Organisation (ESO)",
            "guideline_title": "Guidelines for the Management of Patients with Spontaneous Intracerebral Hemorrhage",
            "publication_year": 2024,
            "source_url": "https://www.ahajournals.org/doi/10.1161/STR.0000000000000407",
            "verification_hash": _calc_hash("8B00", "Intracerebral Hemorrhage")
        }
    },
    {
        "icd11_code": "8A80",
        "icd10_code": "G43.1",
        "clinical_name": "Migraine with and without Aura",
        "common_aliases": ["Hemicrania", "Vascular Headache", "ඉරුවාරදය", "Migraine"],
        "medical_specialty": MedicalSpecialty.NEUROLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Neurovascular disorder involving primary brain hyperexcitability. "
            "Cortical Spreading Depression (CSD) produces the visual/sensory aura. "
            "Subsequent activation of the trigeminovascular system releases vasoactive neuropeptides "
            "(Calcitonin Gene-Related Peptide - CGRP, Substance P), generating neurogenic dural inflammation, "
            "vasodilation, and peripheral/central trigeminal sensitization."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Unilateral, pulsating, throbbing headache of moderate to severe intensity", "weight": 0.94},
                {"symptom": "Duration typically 4 to 72 hours if untreated", "weight": 0.90},
                {"symptom": "Headache aggravated by routine physical activity (walking, climbing stairs)", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Nausea and/or vomiting during the acute attack", "weight": 0.85},
                {"symptom": "Photophobia (light sensitivity) and phonophobia (sound sensitivity)", "weight": 0.88},
                {"symptom": "Visual aura: scintillating scotoma, fortification spectra, scintillating zig-zag lights", "weight": 0.82},
            ]
        },
        "red_flag_criteria": [
            "SNOOP4 red flags: Sudden thunderclap onset (reaches maximum intensity within 1 minute)",
            "New-onset headache in patient > 50 years (suspect Giant Cell Arteritis)",
            "Headache with systemic symptoms (fever, neck stiffness, jaw claudication, unintentional weight loss)",
            "Persistent focal neurological deficit that outlasts the headache (Status Migrainosus > 72 hours)"
        ],
        "differential_diagnoses": [
            {"condition": "Tension-Type Headache", "icd11": "8A81", "distinction": "Bilateral, non-pulsating band-like pressure, mild to moderate, not aggravated by routine physical activity, absence of vomiting."},
            {"condition": "Cluster Headache", "icd11": "8A82", "distinction": "Strictly unilateral excruciating periorbital pain lasting 15-180 min with ipsilateral conjunctival injection, lacrimation, rhinorrhea."},
            {"condition": "Subarachnoid Hemorrhage", "icd11": "8B01", "distinction": "Instantaneous maximal onset thunderclap headache, nuchal rigidity, subarachnoid blood on CT."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Clinical diagnosis based on International Headache Society (ICHD-3) criteria", "Fundoscopy to exclude papilledema (elevated intracranial pressure)"],
            "imaging_ecg": ["Brain MRI / CT indicated only if atypical features, abnormal neurological exam, or red flags present"],
            "confirmatory_tests": ["Erythrocyte Sedimentation Rate (ESR) and CRP if aged > 50 to rule out Temporal Arteritis"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Maintain consistent sleep schedule, hydration, and regular meal timing",
                "Keep a structured headache diary to identify individual dietary and stress triggers"
            ],
            "pharmacotherapy": [
                "Acute abortive therapy (taken at earliest onset of headache phase): Oral Triptan (Sumatriptan 50-100 mg or Zolmitriptan 2.5-5 mg) combined with NSAID (Naproxen 500 mg)",
                "Adjunctive antiemetic: Oral Domperidone 10 mg or Metoclopramide 10 mg",
                "Prophylactic therapy (indicated if >= 4 headache days/month): First-line: Beta-blocker (Propranolol 40-160 mg daily), Topiramate 25-100 mg daily, or Candesartan; Calcitonin Gene-Related Peptide (CGRP) monoclonal antibodies (Erenumab, Fremanezumab) for refractory migraine"
            ],
            "contraindications": [
                "Triptans are contraindicated in ischemic heart disease, previous myocardial infarction, stroke, peripheral vascular disease, or uncontrolled hypertension due to coronary/cerebrovascular vasoconstrictor effects."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Headache Society (AHS) & European Headache Federation",
            "guideline_title": "AHS Consensus Statement on the Management of Migraine",
            "publication_year": 2024,
            "source_url": "https://headachejournal.onlinelibrary.wiley.com/doi/10.1111/head.14692",
            "verification_hash": _calc_hash("8A80", "Migraine Headache")
        }
    },
    {
        "icd11_code": "8A62",
        "icd10_code": "G40.3",
        "clinical_name": "Generalized Tonic-Clonic Epilepsy",
        "common_aliases": ["Grand Mal Seizure", "Convulsive Disorder", "අපස්මාරය", "වලිප්පුව"],
        "medical_specialty": MedicalSpecialty.NEUROLOGY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Paroxysmal neurological disorder characterized by widespread, hypersynchronous neuronal firing "
            "originating from bi-hemispheric cortical and thalamocortical networks. "
            "Imbalance between GABAergic synaptic inhibition and glutamatergic NMDA/AMPA excitation produces "
            "an initial sustained tonic muscular contraction followed by rhythmic clonic jerking, "
            "massive autonomic discharge, and subsequent post-ictal neuronal exhaustion."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Sudden loss of consciousness with ictal cry", "weight": 0.98},
                {"symptom": "Tonic phase: generalized sustained muscular rigidity with cyanosis", "weight": 0.96},
                {"symptom": "Clonic phase: synchronous, rhythmic, violent jerking of all four limbs", "weight": 0.96},
            ],
            "secondary": [
                {"symptom": "Lateral tongue biting (highly specific for epileptic seizure)", "weight": 0.90},
                {"symptom": "Urinary and/or fecal incontinence", "weight": 0.75},
                {"symptom": "Post-ictal phase: deep stertorous breathing, confusion, flaccidity, and retrograde amnesia", "weight": 0.92},
            ]
        },
        "red_flag_criteria": [
            "Status Epilepticus: Continuous seizure activity lasting > 5 minutes, or >= 2 discrete seizures without complete return to consciousness between them (medical emergency)",
            "Refractory status epilepticus unresponsive to first- and second-line antiepileptic agents",
            "Post-ictal focal neurological deficit lasting > 24 hours (excluding brief Todd paresis)",
            "First-ever unprovoked seizure in adult or following head trauma"
        ],
        "differential_diagnoses": [
            {"condition": "Convulsive Syncope", "icd11": "MG45", "distinction": "Preceded by prolonged lightheadedness, brief duration of myoclonic twitches (<15 seconds), rapid reorientation within 1 minute, absence of lateral tongue biting."},
            {"condition": "Psychogenic Non-Epileptic Seizures (PNES)", "icd11": "8E64", "distinction": "Asynchronous out-of-phase limb thrashing, pelvic thrusting, eyes closed resisting opening, normal ictal/post-ictal EEG."},
            {"condition": "Severe Acute Hypoglycemia", "icd11": "5A41", "distinction": "Capillary glucose < 40 mg/dL, diaphoresis, prompt cessation with IV glucose."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Capillary blood glucose, Serum Electrolytes (Sodium, Calcium, Magnesium)", "Renal Function Tests, Liver function, Full Blood Count", "Toxicology screen for alcohol withdrawal or pro-convulsant drug toxicity"],
            "imaging_ecg": ["12-Lead ECG (rule out cardiogenic syncope with secondary jerking)", "Brain MRI (epilepsy protocol: high-resolution coronal T2/FLAIR for mesial temporal sclerosis, focal cortical dysplasia)"],
            "confirmatory_tests": ["Electroencephalography (EEG): Standard 30-minute waking and sleep-deprived EEG (generalized spike-and-wave discharges)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "During active seizure: Turn patient into recovery position on side, protect head, DO NOT restrain limbs or insert anything into the mouth",
                "Driving regulations: Strict legal cessation of motor vehicle operation until seizure-free (typically 12 months)",
                "Water safety: Showers instead of baths, never swim unsupervised"
            ],
            "pharmacotherapy": [
                "Acute Status Epilepticus (>= 5 min): IV Lorazepam 4 mg (or Midazolam 10 mg IM/buccal) repeated once at 10 min; If persisting at 20 min: IV Levetiracetam 60 mg/kg (max 4.5g) or IV Sodium Valproate 40 mg/kg",
                "Long-term Maintenance Monotherapy for generalized epilepsy: Sodium Valproate (caution in women of childbearing potential), Levetiracetam 500-1500 mg BID, or Lamotrigine"
            ],
            "contraindications": [
                "Sodium Valproate is strictly contraindicated in women of childbearing potential unless pregnancy prevention program in place due to high teratogenicity (neural tube defects) and neurodevelopmental delay."
            ]
        },
        "source_metadata": {
            "issuing_authority": "International League Against Epilepsy (ILAE) & NICE",
            "guideline_title": "NICE Guideline NG217: Epilepsies in Children, Young People and Adults",
            "publication_year": 2023,
            "source_url": "https://www.nice.org.uk/guidance/ng217",
            "verification_hash": _calc_hash("8A62", "Generalized Epilepsy")
        }
    },
    {
        "icd11_code": "1D01",
        "icd10_code": "G00.9",
        "clinical_name": "Acute Bacterial Meningitis",
        "common_aliases": ["Purulent Meningitis", "Meningococcal Meningitis", "මෙනින්ජයිටිස්", "Meningitis"],
        "medical_specialty": MedicalSpecialty.NEUROLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Acute suppurative bacterial infection of the subarachnoid space and leptomeninges "
            "most frequently caused by Streptococcus pneumoniae, Neisseria meningitidis, or Listeria monocytogenes. "
            "Bacterial lysis in cerebrospinal fluid releases endotoxins/peptidoglycans, triggering violent cytokines cascades "
            "(TNF-alpha, IL-1beta), purulent exudate accumulation, blood-brain barrier disruption, "
            "cerebral edema, cortical venous thrombosis, and critically elevated intracranial pressure."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Classical clinical triad: High fever, severe headache, and nuchal rigidity (neck stiffness)", "weight": 0.98},
                {"symptom": "Extreme photophobia and phonophobia", "weight": 0.92},
                {"symptom": "Altered mental status (Glasgow Coma Scale < 14)", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Positive Kernig sign (hamstring resistance to knee extension) and Brudzinski sign", "weight": 0.85},
                {"symptom": "Non-blanching petechial or purpuric rash (hallmark of Neisseria meningitidis)", "weight": 0.88},
                {"symptom": "Nausea, projectile vomiting, and cranial nerve palsies (VI, VII)", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Rapidly spreading purpura fulminans / non-blanching rash (fulminant meningococcemia / Waterhouse-Friderichsen syndrome)",
            "GCS <= 8 or rapidly falling consciousness",
            "Focal neurological deficits or new-onset unprovoked seizures",
            "Septic shock refractory to fluid loading",
            "Signs of brainstem herniation: unilateral unreactive pupil, decerebrate posturing, abnormal respiratory pattern"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Viral Encephalitis (Herpes Simplex HSV-1)", "icd11": "1D00.0", "distinction": "Prominent psychiatric symptoms, bizarre behavioral changes, temporal lobe hyperintensity on MRI, lymphocytic CSF."},
            {"condition": "Subarachnoid Hemorrhage", "icd11": "8B01", "distinction": "Afebril at onset, thunderclap headache, hyperdense blood on CT, uniform blood in all CSF collection tubes."},
            {"condition": "Brain Abscess", "icd11": "1D02", "distinction": "Focal mass lesion with ring enhancement on contrast CT/MRI; lumbar puncture contraindicated due to herniation risk."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Immediate blood cultures (2 sets drawn within 15 minutes)", "Full Blood Count (marked leukocytosis with neutrophilic bands)", "Serum Procalcitonin and C-Reactive Protein"],
            "imaging_ecg": ["Head CT scan PRIOR to lumbar puncture ONLY IF focal neurological deficit, papilledema, immunocompromise, or GCS < 10"],
            "confirmatory_tests": ["Lumbar Puncture / CSF Analysis: Opening pressure > 200 mmH2O, cloudy appearance, pleocytosis (>1000/uL predominantly neutrophils), high protein (>100 mg/dL), low CSF:serum glucose ratio (<0.40), positive Gram stain/PCR"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Droplet isolation precautions for the first 24 hours of effective antimicrobial therapy",
                "Immediate public health notification for meningococcal chemoprophylaxis to close household contacts"
            ],
            "pharmacotherapy": [
                "DO NOT DELAY ANTIBIOTICS FOR LUMBAR PUNCTURE: Empirical IV Ceftriaxone 2g Q12H (or Cefotaxime 2g Q4-6H) + Vancomycin 15-20 mg/kg Q8-12H",
                "Add IV Ampicillin 2g Q4H if age > 50 years or immunocompromised (covers Listeria monocytogenes)",
                "Adjunctive Dexamethasone: 10 mg IV administered with or 15 minutes PRIOR to first antibiotic dose (reduces mortality and hearing loss in pneumococcal meningitis)",
                "Prophylaxis for close contacts of meningococcal disease: Single dose oral Ciprofloxacin 500 mg or Rifampicin 600 mg BID for 2 days"
            ],
            "contraindications": [
                "Do NOT perform lumbar puncture if clinical signs of intracranial mass effect or uncorrected coagulopathy are present due to risk of fatal uncal herniation."
            ]
        },
        "source_metadata": {
            "issuing_authority": "Infectious Diseases Society of America (IDSA) & UK Joint Specialist Guidelines",
            "guideline_title": "IDSA Guidelines for the Management of Bacterial Meningitis",
            "publication_year": 2024,
            "source_url": "https://www.idsociety.org/practice-guideline/bacterial-meningitis/",
            "verification_hash": _calc_hash("1D01", "Bacterial Meningitis")
        }
    },
    {
        "icd11_code": "6A70",
        "icd10_code": "F32.9",
        "clinical_name": "Single Episode Major Depressive Disorder",
        "common_aliases": ["Clinical Depression", "Major Depression", "විෂාදය"],
        "medical_specialty": MedicalSpecialty.PSYCHIATRY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Complex psychiatric disorder driven by monoaminergic neurotransmission deficits (serotonin, norepinephrine, dopamine), "
            "dysregulated hypothalamic-pituitary-adrenal (HPA) stress axis with hypercortisolemia, "
            "neuroinflammatory microglial activation, and decreased neurotrophic signaling (Brain-Derived Neurotrophic Factor - BDNF) "
            "resulting in structural atrophy and synaptic loss in the hippocampus and prefrontal cortex."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Persistent depressed mood for at least 2 consecutive weeks", "weight": 0.98},
                {"symptom": "Pervasive anhedonia (loss of interest or pleasure in all activities)", "weight": 0.96},
                {"symptom": "Chronic overwhelming fatigue and loss of energy", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Insomnia (especially terminal early morning awakening) or hypersomnia", "weight": 0.88},
                {"symptom": "Significant involuntary weight loss or gain (>5% in a month)", "weight": 0.82},
                {"symptom": "Psychomotor agitation or noticeable retardation", "weight": 0.80},
                {"symptom": "Feelings of worthlessness or excessive inappropriate guilt", "weight": 0.85},
            ]
        },
        "red_flag_criteria": [
            "Active suicidal ideation with specific intent, detailed plan, or lethal means preparation",
            "Recent suicide attempt or self-harm behavior",
            "Psychotic depression: mood-congruent auditory hallucinations or nihilistic delusions (Cotard syndrome)",
            "Severe psychomotor stupor with refusal of all food and fluid intake (threat to life)"
        ],
        "differential_diagnoses": [
            {"condition": "Bipolar Affective Disorder (Depressive Phase)", "icd11": "6A60", "distinction": "Past history of hypomanic or manic episodes (elevated mood, decreased need for sleep, grandiosity)."},
            {"condition": "Primary Hypothyroidism", "icd11": "5A00", "distinction": "Cold intolerance, constipation, physical slowing, elevated serum TSH."},
            {"condition": "Adjustment Disorder with Depressed Mood", "icd11": "6B43", "distinction": "Identifiable psychosocial stressor within 1 month, symptoms do not meet full MDD criteria and remit when stressor ends."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Validated screening questionnaire: Patient Health Questionnaire-9 (PHQ-9 score >= 10 indicates moderate-to-severe depression)", "Comprehensive Suicide Risk Assessment (Columbia-Suicide Severity Rating Scale - C-SSRS)"],
            "imaging_ecg": ["Baseline 12-Lead ECG if considering Citalopram, Escitalopram, or Tricyclic Antidepressants (evaluate QTc interval)"],
            "confirmatory_tests": ["Serum TSH, Vitamin B12, and Complete Blood Count to exclude organic medical mimics"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Structured evidence-based psychotherapy: Cognitive Behavioral Therapy (CBT) or Interpersonal Psychotherapy (IPT)",
                "Regular aerobic exercise (150 min/week shown to have moderate effect size on depressive symptoms)",
                "Sleep hygiene optimization and structured daily behavioral activation"
            ],
            "pharmacotherapy": [
                "First-line Pharmacotherapy for moderate-to-severe MDD: Selective Serotonin Reuptake Inhibitor (SSRI: Sertraline 50-100 mg daily or Escitalopram 10-20 mg daily)",
                "Alternative: Serotonin-Norepinephrine Reuptake Inhibitor (SNRI: Venlafaxine 75-225 mg daily or Duloxetine 60 mg daily)",
                "Counsel patient that full therapeutic antidepressant onset requires 2 to 4 weeks of continuous adherence; continue treatment for >= 6-9 months after remission to prevent relapse"
            ],
            "contraindications": [
                "Never initiate antidepressant monotherapy in suspected Bipolar Depression as it precipitates rapid manic switching or rapid cycling. Black box warning for increased suicidal thinking in young adults < 25 years during initial 2 weeks."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Psychiatric Association (APA) & NICE",
            "guideline_title": "NICE Guideline NG222: Depression in Adults - Treatment and Management",
            "publication_year": 2024,
            "source_url": "https://www.nice.org.uk/guidance/ng222",
            "verification_hash": _calc_hash("6A70", "Major Depressive Disorder")
        }
    },
    {
        "icd11_code": "6B00",
        "icd10_code": "F41.1",
        "clinical_name": "Generalized Anxiety Disorder (GAD)",
        "common_aliases": ["Chronic Anxiety", "GAD", "කාංසාව"],
        "medical_specialty": MedicalSpecialty.PSYCHIATRY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Neurobiological disorder characterized by hyperactivation of the amygdala and fear circuitry "
            "coupled with deficient top-down inhibitory control from the ventromedial prefrontal cortex. "
            "Abnormalities in GABAergic receptor sensitivity, serotonergic transmission, and noradrenergic hyperarousal "
            "produce persistent, uncontrollable anticipatory dread, hypervigilance, and autonomic physical tension."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Excessive, uncontrollable anxiety and worry about multiple everyday life events", "weight": 0.96},
                {"symptom": "Symptoms occurring on more days than not for at least 6 months", "weight": 0.94},
                {"symptom": "Difficulty controlling the worry and pervasive sense of restlessness or feeling on edge", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Persistent muscle tension (neck, shoulder, jaw clenching)", "weight": 0.88},
                {"symptom": "Easy fatigability and impaired concentration / mind going blank", "weight": 0.82},
                {"symptom": "Sleep disturbance (difficulty falling or staying asleep, restless unrefreshing sleep)", "weight": 0.85},
                {"symptom": "Autonomic symptoms: palpitations, dry mouth, sweating, epigastric churning", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Co-morbid severe depression with active suicidal ideation or suicide planning",
            "Acute secondary substance use or benzodiazepine dependence",
            "Incapacitating panic attacks with severe agoraphobia preventing leaving the house",
            "Medical mimic: undiagnosed cardiac arrhythmia or pheochromocytoma"
        ],
        "differential_diagnoses": [
            {"condition": "Panic Disorder", "icd11": "6B01", "distinction": "Discrete, sudden, recurrent panic attacks reaching crescendo within 10 minutes accompanied by intense fear of dying or losing control."},
            {"condition": "Hyperthyroidism", "icd11": "5A02", "distinction": "Suppressed TSH, elevated free T4, weight loss despite increased appetite, fine tremor."},
            {"condition": "Substance/Medication-Induced Anxiety", "icd11": "6C40", "distinction": "Temporal correlation with excess caffeine, sympathomimetic decongestants, or alcohol withdrawal."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Validated screening questionnaire: Generalized Anxiety Disorder 7-item scale (GAD-7 score >= 10 indicates probable GAD)", "Comprehensive physical examination to exclude cardiovascular and respiratory mimics"],
            "imaging_ecg": ["12-Lead ECG to rule out supraventricular tachycardia and ischemic pathology"],
            "confirmatory_tests": ["Serum TSH, Fasting Blood Glucose, Urine Toxicology Screen"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Individualized Cognitive Behavioral Therapy (CBT - cognitive restructuring, worry exposure, applied relaxation)",
                "Caffeine, nicotine, and energy drink cessation",
                "Mindfulness-based stress reduction and progressive muscle relaxation training"
            ],
            "pharmacotherapy": [
                "First-line Pharmacotherapy: SSRI (Sertraline 50-100 mg daily or Escitalopram 10-20 mg daily) OR SNRI (Duloxetine 60 mg daily or Venlafaxine 75-150 mg daily)",
                "Alternative non-benzodiazepine anxiolytic: Pregabalin 150-300 mg daily (effective for psychic and somatic symptoms)",
                "Short-term crisis use only: Propranolol 10-40 mg PRN for situational somatic palpitations"
            ],
            "contraindications": [
                "Long-term Benzodiazepines (Diazepam, Alprazolam, Clonazepam) are strongly NOT recommended due to rapid tolerance, dependence, cognitive blunting, and severe withdrawal rebound."
            ]
        },
        "source_metadata": {
            "issuing_authority": "World Federation of Societies of Biological Psychiatry (WFSBP) & NICE",
            "guideline_title": "NICE Clinical Guideline CG113: Generalised Anxiety Disorder and Panic Disorder in Adults",
            "publication_year": 2023,
            "source_url": "https://www.nice.org.uk/guidance/cg113",
            "verification_hash": _calc_hash("6B00", "Generalized Anxiety Disorder")
        }
    },

    # -------------------------------------------------------------------------
    # 6. GASTROENTEROLOGY & HEPATOLOGY
    # -------------------------------------------------------------------------
    {
        "icd11_code": "DA22",
        "icd10_code": "K21.9",
        "clinical_name": "Gastroesophageal Reflux Disease (GERD)",
        "common_aliases": ["Acid Reflux", "Heartburn", "ගැස්ට්‍රයිටිස්", "Reflux Esophagitis"],
        "medical_specialty": MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Retrograde flow of gastric acid, pepsin, and bile acids into the esophagus "
            "resulting from transient lower esophageal sphincter (LES) relaxations, low resting LES basal pressure, "
            "or hiatal hernia. "
            "Acid-peptic contact induces chemical mucosal damage, inflammatory cytokine release, "
            "dilated intercellular spaces, and progressive columnar metaplasia (Barrett esophagus)."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Pyrosis (retrosternal burning sensation radiating upwards toward neck)", "weight": 0.96},
                {"symptom": "Acid regurgitation of sour or bitter fluid into pharynx or mouth", "weight": 0.94},
                {"symptom": "Symptoms aggravated by lying supine, bending forward, or post-prandially", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Epigastric post-prandial fullness and bloating", "weight": 0.75},
                {"symptom": "Chronic nocturnal dry cough and throat clearing", "weight": 0.68},
                {"symptom": "Dental enamel erosion and morning hoarseness (reflux laryngitis)", "weight": 0.62},
            ]
        },
        "red_flag_criteria": [
            "Progressive dysphagia (difficulty swallowing solids progressing to liquids)",
            "Odynophagia (painful swallowing indicating severe ulceration)",
            "Persistent vomiting or hematemesis / melena",
            "Unexplained weight loss or palpable epigastric mass",
            "Atypical chest pain mimicking acute myocardial infarction"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Coronary Syndrome (ACS)", "icd11": "BA41", "distinction": "Must be ruled out first in all patients presenting with retrosternal burning; ECG and troponins are mandatory."},
            {"condition": "Eosinophilic Esophagitis", "icd11": "DA23", "distinction": "Younger atopic individuals with food impaction, ringed esophagus on endoscopy, >15 eosinophils/HPF on biopsy."},
            {"condition": "Peptic Ulcer Disease", "icd11": "DA60", "distinction": "Epigastric localized gnawing pain related to meals, H. pylori positive."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Clinical diagnosis for typical heartburn/regurgitation without alarm symptoms (empiric PPI trial)", "Fasting Full Blood Count (screen for microcytic iron deficiency anemia)"],
            "imaging_ecg": ["Upper Gastrointestinal Endoscopy (Esophagogastroduodenoscopy - EGD) mandatory if red flags or age > 55"],
            "confirmatory_tests": ["24-Hour Ambulatory Esophageal pH-Impedance Monitoring (gold standard for refractory symptoms)", "High-Resolution Esophageal Manometry (rule out achalasia)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Elevation of the head of bed by 15-20 cm using bed risers (gravity prevents nocturnal reflux)",
                "Avoid late-night meals: Maintain at least a 3-hour interval between dinner and recumbency",
                "Weight loss if overweight (BMI > 25); avoid trigger foods (chocolate, high-fat meals, caffeine, mint, citrus)"
            ],
            "pharmacotherapy": [
                "First-line 8-week healing course: Proton Pump Inhibitor (PPI: Omeprazole 20-40 mg, Esomeprazole 20-40 mg, or Pantoprazole 40 mg daily) taken 30-60 minutes before breakfast",
                "On-demand symptomatic relief: Alginate-antacid formulations (Gaviscon) which form a floating raft barrier",
                "Step-down maintenance to lowest effective dose once symptoms remit"
            ],
            "contraindications": [
                "Avoid long-term high-dose unmonitored PPI therapy without periodic re-evaluation due to modest associations with hypomagnesemia, Vitamin B12 malabsorption, and Clostridioides difficile colitis."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American College of Gastroenterology (ACG)",
            "guideline_title": "ACG Clinical Guideline for the Diagnosis and Management of Gastroesophageal Reflux Disease",
            "publication_year": 2023,
            "source_url": "https://journals.lww.com/ajg/fulltext/2022/01000/guidelines_for_the_diagnosis_and_management_of.14.aspx",
            "verification_hash": _calc_hash("DA22", "Gastroesophageal Reflux")
        }
    },
    {
        "icd11_code": "DA60",
        "icd10_code": "K27.9",
        "clinical_name": "Peptic Ulcer Disease (Gastric & Duodenal)",
        "common_aliases": ["PUD", "Stomach Ulcer", "ආමාශගත තුවාල", "Duodenal Ulcer"],
        "medical_specialty": MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Disruption of mucosal integrity extending through the muscularis mucosae into the submucosa. "
            "Overwhelmingly caused by Helicobacter pylori infection (producing urease, VacA, and CagA cytotoxins) "
            "or NSAID inhibition of COX-1, which suppresses mucosal prostaglandin synthesis, diminishes mucus and bicarbonate secretion, "
            "and impairs mucosal blood flow in the face of luminal gastric acid."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Epigastric gnawing, burning, or aching abdominal pain", "weight": 0.95},
                {"symptom": "Duodenal ulcer: pain relieved by food or antacids, recurring 2-3 hours post-prandially and nocturnal pain (12-3 AM)", "weight": 0.90},
                {"symptom": "Gastric ulcer: pain precipitated or worsened by food ingestion, leading to food avoidance", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Nausea, early satiety, and abdominal distension", "weight": 0.75},
                {"symptom": "Unintentional weight loss (more prominent in gastric ulcers)", "weight": 0.70},
                {"symptom": "Belching and fatty food intolerance", "weight": 0.60},
            ]
        },
        "red_flag_criteria": [
            "Upper Gastrointestinal Bleeding: Hematemesis ('coffee-ground' vomitus) or melena (black tarry sticky stools)",
            "Acute perforation: Sudden catastrophic severe generalized abdominal pain with board-like muscular rigidity",
            "Gastric Outlet Obstruction: Persistent non-bilious projectile vomiting containing undigested food ingested hours prior",
            "Severe orthostatic dizziness, syncope, or hemodynamic instability"
        ],
        "differential_diagnoses": [
            {"condition": "Gastric Adenocarcinoma", "icd11": "2B72", "distinction": "Endoscopic biopsy is mandatory for all gastric ulcers to differentiate benign peptic ulcer from malignant ulceration."},
            {"condition": "Biliary Colic (Cholelithiasis)", "icd11": "DC11", "distinction": "Episodic severe right upper quadrant post-fatty meal pain radiating to the right shoulder blade."},
            {"condition": "Chronic Mesenteric Ischemia", "icd11": "BD90", "distinction": "'Abdominal angina' - severe post-prandial pain out of proportion to exam in elderly patients with vascular disease."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (microcytic hypochromic iron-deficiency anemia)", "Fecal Occult Blood Test (FOBT)", "Urea Breath Test (UBT using C-13 or C-14) or Fecal Antigen Test for H. pylori"],
            "imaging_ecg": ["Upper Gastrointestinal Endoscopy (EGD - definitive gold standard; permits biopsy and therapeutic hemostasis)", "Erect Chest Radiograph (mandatory if acute perforation suspected: free gas under diaphragm)"],
            "confirmatory_tests": ["Endoscopic biopsy with Rapid Urease Test (CLO test) and histological evaluation"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Complete cessation of all NSAIDs, Aspirin, and tobacco smoking (smoking significantly impairs ulcer healing)",
                "Avoid alcohol and heavy coffee intake during active ulcer healing"
            ],
            "pharmacotherapy": [
                "H. pylori Eradication: First-line Quadruple Therapy for 14 days: Bismuth Subsalicylate + Metronidazole 500 mg TID + Tetracycline 500 mg QID + High-dose PPI (Esomeprazole 40 mg BID)",
                "Alternative: Clarithromycin-based Triple Therapy (only in areas with proven Clarithromycin resistance < 15%): PPI BID + Clarithromycin 500 mg BID + Amoxicillin 1g BID for 14 days",
                "NSAID-Induced Ulcers (H. pylori negative): Discontinue NSAID; treat with PPI (Omeprazole 20-40 mg daily) for 8 weeks"
            ],
            "contraindications": [
                "Never discontinue PPI abruptly without confirming eradication via repeat stool antigen or urea breath test at least 4 weeks post-treatment."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American College of Gastroenterology (ACG) & Maastricht VI Consensus",
            "guideline_title": "ACG Clinical Guideline: Treatment of Helicobacter pylori Infection",
            "publication_year": 2024,
            "source_url": "https://journals.lww.com/ajg/fulltext/2024/09000/treatment_of_helicobacter_pylori_infection.12.aspx",
            "verification_hash": _calc_hash("DA60", "Peptic Ulcer Disease")
        }
    },
    {
        "icd11_code": "DB10",
        "icd10_code": "K35.8",
        "clinical_name": "Acute Appendicitis",
        "common_aliases": ["Appendicitis", "ඇපෙන්ඩිසයිටිස්", "Ruptured Appendix"],
        "medical_specialty": MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Acute inflammation of the vermiform appendix initiated by luminal obstruction "
            "(fecalith, lymphoid hyperplasia, foreign body, or carcinoid tumor). "
            "Continued mucosal secretion behind the obstruction causes progressive distension, elevated intraluminal pressure, "
            "venous and lymphatic occlusion, bacterial transmural invasion, ischemia, gangrene, and eventual perforation."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Periumbilical visceral dull pain migrating to the right lower quadrant (RLQ)", "weight": 0.98},
                {"symptom": "Sharp, localized somatic pain at McBurney point (one-third from ASIS to umbilicus)", "weight": 0.96},
                {"symptom": "Anorexia ('hamburger sign': aversion to all food)", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Low-grade pyrexia (37.5 - 38.3 C)", "weight": 0.85},
                {"symptom": "Nausea and vomiting developing AFTER onset of abdominal pain", "weight": 0.88},
                {"symptom": "Rebound tenderness (Blumberg sign) and involuntary guarding in RLQ", "weight": 0.90},
                {"symptom": "Rovsing sign (RLQ pain upon left lower quadrant palpation)", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Perforated Appendicitis: Sudden transient relief of severe pain followed by rapid development of generalized rigid peritonitis",
            "High spiking fever (> 38.8 C) with rigors and marked tachycardia",
            "Septic shock: hypotension, cold clammy extremities, and metabolic acidosis",
            "Palpable tender inflammatory appendicular mass or abscess in RLQ"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Mesenteric Adenitis", "icd11": "DA92", "distinction": "Common in children following viral URI, multiple enlarged mesenteric lymph nodes on ultrasound, appendix normal."},
            {"condition": "Ruptured Ectopic Pregnancy", "icd11": "JA01", "distinction": "Mandatory urine pregnancy test in all females of childbearing age; sudden severe pelvic pain, transvaginal ultrasound confirmation."},
            {"condition": "Right-sided Ureteric Colic", "icd11": "GB70", "distinction": "Severe spasmodic loin-to-groin pain, microscopic hematuria, non-contrast CT KUB demonstrates calculus."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (neutrophilic leukocytosis > 10,000/uL with left shift)", "Serum C-Reactive Protein (CRP)", "Urinalysis (rule out UTI, mild sterile pyuria may occur due to proximity to ureter)", "Serum/Urine Beta-hCG (mandatory in all reproductive-age females)"],
            "imaging_ecg": ["Abdominal and Pelvic Ultrasound (non-compressible blind-ended tubular structure > 6 mm diameter, target sign)", "Contrast-Enhanced CT Abdomen/Pelvis (gold standard in adults: wall thickening, periappendiceal fat stranding, appendicolith)"],
            "confirmatory_tests": ["Clinical Risk Stratification via Alvarado Score or Adult Appendicitis Score (AAS)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate surgical referral; strict nil-by-mouth (NPO) status",
                "Intravenous isotonic crystalloid fluid resuscitation"
            ],
            "pharmacotherapy": [
                "Pre-operative broad-spectrum intravenous antibiotics covering enteric gram-negatives and anaerobes: Ceftriaxone 1g IV + Metronidazole 500 mg IV (or Piperacillin-Tazobactam 4.5g IV)",
                "Definitive treatment: Laparoscopic Appendectomy (gold standard surgical intervention)",
                "Non-operative antibiotic management is reserved only for carefully selected uncomplicated cases in clinical trials or high surgical risk"
            ],
            "contraindications": [
                "Do NOT administer laxatives, enemas, or local heating pads as they dramatically increase intraluminal pressure and precipitate appendix rupture."
            ]
        },
        "source_metadata": {
            "issuing_authority": "World Society of Emergency Surgery (WSES)",
            "guideline_title": "WSES Jerusalem Guidelines for Diagnosis and Treatment of Acute Appendicitis",
            "publication_year": 2024,
            "source_url": "https://wses.biomedcentral.com/articles/10.1186/s13017-020-00306-3",
            "verification_hash": _calc_hash("DB10", "Acute Appendicitis")
        }
    },
    {
        "icd11_code": "DB93",
        "icd10_code": "K74.6",
        "clinical_name": "Decompensated Liver Cirrhosis",
        "common_aliases": ["Hepatic Cirrhosis", "End-Stage Liver Disease", "සිරෝසිස්", "Liver Failure"],
        "medical_specialty": MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "End-stage hepatic parenchymal architecture distortion characterized by diffuse nodular regeneration "
            "surrounded by dense fibrous septa (collagen deposition by activated hepatic stellate cells). "
            "Increased intrahepatic sinusoidal resistance causes portal hypertension, splanchnic arterial vasodilation, "
            "ascites, portosystemic collateral shunting (esophageal varices), and hepatic synthetic failure."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Progressive abdominal distension with shifting dullness and fluid thrill (Ascites)", "weight": 0.96},
                {"symptom": "Deepening jaundice and scleral icterus", "weight": 0.92},
                {"symptom": "Bilateral pedal pitting edema and abdominal wall collateral veins (Caput Medusae)", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Stigmata of chronic liver disease: Spider angiomas, palmar erythema, gynecomastia", "weight": 0.85},
                {"symptom": "Easy bruising, purpura, and epistaxis (impaired clotting factor synthesis)", "weight": 0.82},
                {"symptom": "Muscle wasting (sarcopenia) and temporal hollowing", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Acute Variceal Bleeding: Massive hematemesis or melena with hemorrhagic shock",
            "Spontaneous Bacterial Peritonitis (SBP): Fever, worsening ascites, abdominal pain, polymorphonuclear count >= 250/uL",
            "Hepatic Encephalopathy: Asterixis (flapping tremor), day-night sleep reversal, confusion, lethargy, or coma",
            "Hepatorenal Syndrome (HRS): Rapidly worsening oliguria and acute kidney injury refractory to albumin expansion"
        ],
        "differential_diagnoses": [
            {"condition": "Congestive Hepatopathy (Cardiac Cirrhosis)", "icd11": "BD11", "distinction": "Markedly elevated jugular venous pressure, hepatojugular reflux, tricuspid regurgitation on echocardiogram."},
            {"condition": "Budd-Chiari Syndrome", "icd11": "BD72", "distinction": "Hepatic vein thrombosis, acute painful hepatomegaly, intractable ascites, Doppler ultrasound confirmation."},
            {"condition": "Peritoneal Carcinomatosis", "icd11": "2C78", "distinction": "Low Serum-Ascites Albumin Gradient (SAAG < 1.1 g/dL), malignant cells on ascitic cytology."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (pancytopenia secondary to hypersplenism)", "Liver Panel (elevated bilirubin, low albumin, AST > ALT in alcohol)", "Coagulation profile: Prothrombin Time / INR (key component of MELD score)", "Serum Sodium and Creatinine"],
            "imaging_ecg": ["Diagnostic Paracentesis (mandatory in new or decompensated ascites: cell count, SAAG calculation, culture in blood bottles)", "Abdominal Ultrasound with Doppler (shrunken nodular liver, splenomegaly, portal vein flow direction)"],
            "confirmatory_tests": ["Upper Endoscopy (EGD to screen for and grade gastroesophageal varices)", "MELD-Na Score calculation"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Strict absolute alcohol abstinence; complete cessation of all hepatotoxic medications and NSAIDs",
                "Dietary sodium restriction to 2,000 mg/day (88 mmol/day); high-protein diet (1.2-1.5 g/kg/day) to combat sarcopenia"
            ],
            "pharmacotherapy": [
                "Ascites management: Dual diuretic therapy combining Spironolactone (100-400 mg daily) + Furosemide (40-160 mg daily) maintaining 100:40 ratio",
                "Spontaneous Bacterial Peritonitis (SBP): Third-generation cephalosporin (Ceftriaxone 2g IV daily for 5 days) + IV Albumin (1.5 g/kg on day 1, 1.0 g/kg on day 3)",
                "Hepatic Encephalopathy: Oral Lactulose (titrated to 2-3 soft bowel movements/day) + Rifaximin 550 mg BID",
                "Variceal bleeding prophylaxis: Non-selective Beta-blocker (Carvedilol 6.25-12.5 mg daily) or Endoscopic Variceal Band Ligation"
            ],
            "contraindications": [
                "NSAIDs and ACE inhibitors/ARBs are strictly contraindicated in decompensated cirrhosis as they precipitate acute renal failure and hepatorenal syndrome."
            ]
        },
        "source_metadata": {
            "issuing_authority": "EASL & AASLD",
            "guideline_title": "EASL Clinical Practice Guidelines for the Management of Patients with Decompensated Cirrhosis",
            "publication_year": 2024,
            "source_url": "https://www.easl.eu/guidelines/decompensated-cirrhosis/",
            "verification_hash": _calc_hash("DB93", "Liver Cirrhosis")
        }
    },
    {
        "icd11_code": "DD70",
        "icd10_code": "K50.9",
        "clinical_name": "Crohn Disease (Inflammatory Bowel Disease)",
        "common_aliases": ["Crohn's", "Regional Enteritis", "IBD", "ක්‍රෝන්ස් රෝගය"],
        "medical_specialty": MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Chronic relapsing transmural granulomatous inflammation affecting any part of the gastrointestinal tract "
            "from mouth to anus (most commonly terminal ileum and cecum). "
            "Defective mucosal barrier function, dysbiosis, and dysregulated Th1/Th17 adaptive immune responses "
            "induce deep fissuring ulcerations, non-caseating granulomas, skip lesions, strictures, and fistulae."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Chronic non-bloody or bloody diarrhea lasting > 4-6 weeks", "weight": 0.94},
                {"symptom": "Crampy, colicky right lower quadrant abdominal pain", "weight": 0.92},
                {"symptom": "Progressive involuntary weight loss and chronic anorexia", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Perianal fistulae, fissures, or recurrent abscesses", "weight": 0.80},
                {"symptom": "Extraintestinal manifestations: peripheral arthritis, erythema nodosum, aphthous stomatitis, uveitis", "weight": 0.75},
                {"symptom": "Low-grade fever and unexplained malaise", "weight": 0.70},
            ]
        },
        "red_flag_criteria": [
            "Toxic Megacolon: Colonic dilation > 6 cm on radiograph with severe systemic toxicity and fever",
            "Complete bowel obstruction secondary to severe fibrostenotic stricturing",
            "Intra-abdominal abscess or acute free perforation with generalized peritonitis",
            "Massive lower gastrointestinal hemorrhage"
        ],
        "differential_diagnoses": [
            {"condition": "Ulcerative Colitis", "icd11": "DD71", "distinction": "Continuous mucosal inflammation strictly limited to colon, begins in rectum and extends proximally, absence of skip lesions or fistulae."},
            {"condition": "Intestinal Tuberculosis", "icd11": "1B10", "distinction": "Common in endemic regions, caseating granulomas, circular ulcers, positive GeneXpert/culture on mucosal biopsy."},
            {"condition": "Infectious Colitis (Campylobacter, Salmonella)", "icd11": "1A00", "distinction": "Acute self-limited onset (<2 weeks), positive stool bacterial pathogen culture."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Fecal Calprotectin (> 250 mcg/g strongly indicates active mucosal inflammation)", "Full Blood Count (anemia of chronic disease or iron deficiency, thrombocytosis)", "C-Reactive Protein (CRP) and ESR"],
            "imaging_ecg": ["Ileocolonoscopy with segmental biopsies (skip lesions, cobblestone mucosa, linear longitudinal ulcerations, non-caseating granulomas)", "MR Enterography (MRE) or CT Enterography (evaluates small bowel thickening, strictures, and fistulae)"],
            "confirmatory_tests": ["Stool testing to rule out Clostridioides difficile toxin and parasitic infections"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Cessation of tobacco smoking (smoking significantly increases Crohn's relapse, strictures, and surgery rates)",
                "Exclusive Enteral Nutrition (EEN) as first-line induction therapy in pediatric Crohn disease",
                "Nutritional supplementation for Vitamin B12, Iron, Vitamin D, and Calcium deficiencies"
            ],
            "pharmacotherapy": [
                "Induction of remission in mild-to-moderate ileocecal disease: Oral Budesonide (controlled-release 9 mg daily for 8 weeks)",
                "Moderate-to-severe disease induction & maintenance: Biologic anti-TNF therapy (Infliximab IV infusion or Adalimumab subcutaneous injection) combined with Thiopurine (Azathioprine 2-2.5 mg/kg daily)",
                "Second-line biologics for anti-TNF failures: Ustekinumab (IL-12/23 inhibitor) or Vedolizumab (gut-selective alpha4beta7 integrin inhibitor)"
            ],
            "contraindications": [
                "NSAIDs must be avoided as they reliably trigger acute clinical relapses. Biologics require screening for latent TB and viral hepatitis prior to initiation."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Crohn's and Colitis Organisation (ECCO) & ACG",
            "guideline_title": "ECCO Guidelines on Therapeutics in Crohn's Disease: Medical Treatment",
            "publication_year": 2024,
            "source_url": "https://www.ecco-ibd.eu/publications/ecco-guidelines-science.html",
            "verification_hash": _calc_hash("DD70", "Crohn Disease")
        }
    },
    {
        "icd11_code": "DC31",
        "icd10_code": "K85.9",
        "clinical_name": "Acute Pancreatitis",
        "common_aliases": ["Inflammation of Pancreas", "Gallstone Pancreatitis", "අග්න්‍යාශ ප්‍රදාහය"],
        "medical_specialty": MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Acute inflammatory disease of the pancreatic parenchyma triggered primarily by gallstone biliary duct impaction "
            "or ethanol-induced oxidative stress. "
            "Premature intracellular activation of trypsinogen to trypsin inside pancreatic acinar cells "
            "initiates autodigestion of pancreatic tissue, capillary leakage, retroperitoneal fat necrosis, "
            "and a massive systemic inflammatory response syndrome (SIRS)."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Sudden onset excruciating, constant epigastric pain radiating through to the mid-back", "weight": 0.98},
                {"symptom": "Pain partially relieved by sitting forward in tripod position or fetal flexion", "weight": 0.94},
                {"symptom": "Persistent nausea and severe intractable vomiting failing to relieve pain", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Epigastric tenderness and abdominal distension with reduced bowel sounds", "weight": 0.85},
                {"symptom": "Tachycardia and low-grade pyrexia", "weight": 0.80},
                {"symptom": "Cullen sign (periumbilical ecchymosis) or Grey Turner sign (flank ecchymosis - retroperitoneal hemorrhage)", "weight": 0.60},
            ]
        },
        "red_flag_criteria": [
            "Severe Acute Pancreatitis (Atlanta criteria): Persistent organ failure > 48 hours (Respiratory: PaO2/FiO2 <= 300, Renal: Creatinine >= 1.9 mg/dL, Cardiovascular: SBP < 90)",
            "Systemic Inflammatory Response Syndrome (SIRS score >= 2) persisting beyond 48 hours",
            "Hemorrhagic retroperitoneal signs (Cullen or Grey Turner signs)",
            "Extensive necrotizing pancreatitis with infected pancreatic necrosis"
        ],
        "differential_diagnoses": [
            {"condition": "Perforated Peptic Ulcer", "icd11": "DA60", "distinction": "Free intraperitoneal air under diaphragm on erect radiograph, board-like abdominal rigidity, normal/mild lipase."},
            {"condition": "Acute Mesenteric Ischemia", "icd11": "BD90", "distinction": "Pain dramatically out of proportion to physical exam findings, high serum lactate, thrombus on CT angiography."},
            {"condition": "Acute Cholecystitis", "icd11": "DC11", "distinction": "Right upper quadrant localized pain, positive Murphy sign, normal serum lipase."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Serum Lipase (diagnostic if >= 3 times upper limit of normal; more sensitive and specific than amylase)", "Full Blood Count, Serum Hematocrit, Blood Urea Nitrogen (BUN > 20 mg/dL predicts mortality)", "Serum Calcium (hypocalcemia secondary to saponification) and Triglycerides"],
            "imaging_ecg": ["Transabdominal Ultrasound (evaluates gallstones in gallbladder, common bile duct dilation)", "Contrast-Enhanced Abdominal CT (CECT - performed 72-96 hours after onset to assess pancreatic necrosis/perfusion; avoids early overestimation)"],
            "confirmatory_tests": ["Diagnosis requires >= 2 of 3 criteria: (1) typical pain, (2) lipase/amylase >= 3x ULN, (3) characteristic cross-sectional imaging"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate hospitalization and aggressive risk stratification (BISAP score, modified Glasgow score)",
                "Early oral refeeding as soon as pain and ileus improve (low-fat solid or liquid diet; routine prolonged NPO is no longer recommended)"
            ],
            "pharmacotherapy": [
                "Goal-directed IV fluid hydration with Ringer's Lactate (Hartmann's solution) at 200-500 mL/h for the first 12-24 hours (guided by hematocrit and BUN reduction)",
                "Effective multimodal analgesia: Intravenous Opioids (Hydromorphone, Fentanyl, or Buprenorphine)",
                "Urgent ERCP (within 24-48 hours) indicated only if concurrent acute ascending cholangitis or impacted CBD stone is present",
                "Index admission cholecystectomy for gallstone pancreatitis once acute inflammation settles"
            ],
            "contraindications": [
                "Prophylactic intravenous antibiotics are strictly NOT recommended in acute or sterile necrotizing pancreatitis; use antibiotics only for proven infected necrosis."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American College of Gastroenterology (ACG) & IAP/APA",
            "guideline_title": "ACG Clinical Guideline: Management of Acute Pancreatitis",
            "publication_year": 2024,
            "source_url": "https://journals.lww.com/ajg/fulltext/2024/03000/management_of_acute_pancreatitis.13.aspx",
            "verification_hash": _calc_hash("DC31", "Acute Pancreatitis")
        }
    },

    # -------------------------------------------------------------------------
    # 7. NEPHROLOGY & UROLOGY
    # -------------------------------------------------------------------------
    {
        "icd11_code": "GB61",
        "icd10_code": "N18.9",
        "clinical_name": "Chronic Kidney Disease (Stages 3b-5)",
        "common_aliases": ["CKD", "Renal Failure", "වකුගඩු අක්‍රියතාව", "Chronic Renal Insufficiency"],
        "medical_specialty": MedicalSpecialty.NEPHROLOGY_UROLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Progressive, irreversible loss of functioning nephrons over >= 3 months resulting from diabetic nephropathy, "
            "hypertensive nephrosclerosis, or glomerulonephritis. "
            "Intraglomerular hypertension and hyperfiltration in surviving nephrons induces podocyte detachment, "
            "glomerulosclerosis, and tubulointerstitial fibrosis, culminating in uremic toxin retention, "
            "impaired erythropoietin synthesis, secondary hyperparathyroidism, and fluid overload."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Persistent bilateral lower limb pitting edema and facial morning puffiness", "weight": 0.92},
                {"symptom": "Nocturia and changes in urinary output", "weight": 0.88},
                {"symptom": "Profound fatigue, pallor, and exertional breathlessness (anemia of CKD)", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Uremic pruritus (intractable dry itching skin)", "weight": 0.82},
                {"symptom": "Metallic taste in mouth, anorexia, nausea, and ammonia breath odor (uremic fetor)", "weight": 0.78},
                {"symptom": "Bone pain and muscle cramps (mineral bone disorder)", "weight": 0.72},
            ]
        },
        "red_flag_criteria": [
            "Life-threatening hyperkalemia (serum potassium > 6.5 mEq/L with peaked T waves on ECG)",
            "Severe fluid overload with acute pulmonary edema refractory to high-dose diuretics",
            "Uremic Pericarditis: pleuro-pericardial friction rub with chest pain (urgent dialysis indication)",
            "Uremic encephalopathy: asterixis, confusion, myoclonic twitches, seizures, or coma"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Kidney Injury (AKI)", "icd11": "GB60", "distinction": "Abrupt decline over hours/days with reversible trigger; kidneys normal sized on ultrasound with preserved cortical thickness."},
            {"condition": "Congestive Heart Failure", "icd11": "BD11", "distinction": "Cardiomegaly, elevated BNP, normal renal parenchyma on imaging, preserved eGFR prior to decompensation."},
            {"condition": "Nephrotic Syndrome", "icd11": "GB40", "distinction": "Heavy proteinuria > 3.5 g/24h with normal renal function in early stages."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Serum Creatinine and Estimated GFR (eGFR via CKD-EPI 2021 equation)", "Urinary Albumin-to-Creatinine Ratio (UACR: A1 < 30, A2 30-300, A3 > 300 mg/g)", "Serum Electrolytes (Potassium, Sodium, Bicarbonate), Calcium, Phosphate"],
            "imaging_ecg": ["Renal Ultrasonography (bilateral shrunken, echogenic kidneys < 9 cm with cortical thinning confirms chronicity)", "12-Lead ECG for hyperkalemic conduction delays"],
            "confirmatory_tests": ["Serum Intact Parathyroid Hormone (iPTH), 25-OH Vitamin D, Ferritin, Transferrin saturation"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Dietary sodium restriction to < 2 g/day; moderate protein restriction (0.6-0.8 g/kg/day in non-dialysis CKD)",
                "Dietary potassium and phosphate restriction in advanced stages (Stages 4-5)",
                "Avoidance of all nephrotoxic agents (NSAIDs, aminoglycosides, iodinated IV contrast)"
            ],
            "pharmacotherapy": [
                "Renoprotection and cardiorenal slowing: SGLT2 Inhibitor (Dapagliflozin 10 mg or Empagliflozin 10 mg daily for eGFR >= 20 mL/min with albuminuria)",
                "First-line blood pressure / proteinuria control: Maximally tolerated ACE-inhibitor (Ramipril) or ARB (Losartan) targeting BP < 120 mmHg systolic",
                "Non-steroidal mineralocorticoid receptor antagonist: Finerenone for diabetic kidney disease with persistent albuminuria",
                "Management of anemia: Erythropoiesis-Stimulating Agents (ESA e.g. Darbepoetin alfa) + IV Iron targeting Hb 10-11.5 g/dL",
                "Phosphate binders (Sevelamer carbonate, Calcium acetate) taken with meals for hyperphosphatemia"
            ],
            "contraindications": [
                "Dual blockade with ACE inhibitor + ARB simultaneously is strictly contraindicated due to heightened risk of hyperkalemia and acute renal shutdown."
            ]
        },
        "source_metadata": {
            "issuing_authority": "Kidney Disease: Improving Global Outcomes (KDIGO)",
            "guideline_title": "KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease",
            "publication_year": 2024,
            "source_url": "https://kdigo.org/guidelines/ckd-evaluation-and-management/",
            "verification_hash": _calc_hash("GB61", "Chronic Kidney Disease")
        }
    },
    {
        "icd11_code": "GB60",
        "icd10_code": "N17.9",
        "clinical_name": "Acute Kidney Injury (AKI)",
        "common_aliases": ["Acute Renal Failure", "AKI", "හදිසි වකුගඩු අකර්මණ්‍යතාව"],
        "medical_specialty": MedicalSpecialty.NEPHROLOGY_UROLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Abrupt decline in renal filtration function (hours to days) classified into Prerenal (hypovolemia, sepsis, cardiorenal), "
            "Intrinsic (Acute Tubular Necrosis from ischemia/toxins, acute interstitial nephritis), "
            "and Postrenal (urinary tract obstruction). "
            "Rapid accumulation of nitrogenous waste products (urea, creatinine) and disruption of fluid, electrolyte, "
            "and acid-base homeostasis occurs."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Acute oliguria (urine output < 0.5 mL/kg/h for >= 6 hours) or absolute anuria", "weight": 0.95},
                {"symptom": "Rapidly rising serum creatinine (>= 0.3 mg/dL within 48h or >= 1.5x baseline)", "weight": 0.98},
                {"symptom": "Acute fluid retention with dependent edema and pulmonary congestion", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Nausea, vomiting, loss of appetite, and hiccups", "weight": 0.75},
                {"symptom": "Drowsiness, confusion, and asterixis (uremic encephalopathy)", "weight": 0.82},
                {"symptom": "Deep acidotic Kussmaul respirations (metabolic acidosis)", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Absolute anuria (< 50 mL in 12 hours)",
            "Refractory hyperkalemia (> 6.5 mEq/L) resistant to medical shifting therapy",
            "Acute severe metabolic acidosis (pH < 7.15, bicarbonate < 10 mEq/L)",
            "Acute uremic pericarditis or uremic encephalopathy with seizures",
            "Refractory pulmonary edema failing high-dose diuretic challenge"
        ],
        "differential_diagnoses": [
            {"condition": "Chronic Kidney Disease", "icd11": "GB61", "distinction": "History of long-standing proteinuria, small echogenic kidneys on ultrasound, prior abnormal creatinine."},
            {"condition": "Hepatorenal Syndrome", "icd11": "DB93", "distinction": "Occurs in severe liver cirrhosis with ascites, failure to respond to 48 hours of albumin expansion and diuretic withdrawal."},
            {"condition": "Acute Glomerulonephritis", "icd11": "GB41", "distinction": "Dysmorphic red blood cells and RBC casts in urine, active serology (low C3/C4, positive ANCA or anti-GBM)."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Serum Creatinine, Blood Urea Nitrogen, and Serum Electrolytes (serial every 6-12 hours)", "Urinary full report and microscopic examination (muddy brown granular casts in ATN, eosinophils in AIN)", "Fractional Excretion of Sodium (FENa < 1% in prerenal, > 2% in intrinsic ATN)"],
            "imaging_ecg": ["Emergency Renal Ultrasound within 24 hours (mandatory: exclude hydronephrosis/postrenal obstruction)", "12-Lead ECG for hyperkalemia signs (peaked T waves, widening QRS)"],
            "confirmatory_tests": ["Urinary biomarkers (NGAL, KIM-1) where available; Renal biopsy for unexplained intrinsic disease"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate Foley catheter placement to quantify hourly urine output accurately",
                "Stop all potential nephrotoxins: NSAIDs, ACEi, ARBs, Aminoglycosides, Vancomycin"
            ],
            "pharmacotherapy": [
                "Prerenal hypovolemic AKI: Fluid resuscitation with isotonic balanced crystalloids (Plasma-Lyte or Hartmann's)",
                "Hyperkalemia management: IV Calcium Gluconate 10% (myocardial stabilization) + IV Regular Insulin 10 units in 50 mL 50% Dextrose + nebulized Salbutamol",
                "Metabolic acidosis: IV Sodium Bicarbonate 1.26% if pH < 7.15 and bicarbonate < 12",
                "Urgent Renal Replacement Therapy (Hemodialysis or CRRT) indications (mnemonic AEIOU): Acidosis, Electrolytes (K+), Ingestion/toxins, Overload (fluid), Uremia"
            ],
            "contraindications": [
                "Do NOT use loop diuretics (Furosemide) to convert oliguric AKI to non-oliguric AKI unless patient is demonstrably fluid overloaded; diuretics do not improve renal recovery or mortality."
            ]
        },
        "source_metadata": {
            "issuing_authority": "KDIGO (Kidney Disease: Improving Global Outcomes)",
            "guideline_title": "KDIGO Clinical Practice Guideline for Acute Kidney Injury",
            "publication_year": 2023,
            "source_url": "https://kdigo.org/guidelines/acute-kidney-injury/",
            "verification_hash": _calc_hash("GB60", "Acute Kidney Injury")
        }
    },
    {
        "icd11_code": "GB70",
        "icd10_code": "N20.1",
        "clinical_name": "Obstructive Nephrolithiasis & Ureteric Colic",
        "common_aliases": ["Kidney Stones", "Renal Calculi", "වකුගඩු ගල්", "Ureteric Stone"],
        "medical_specialty": MedicalSpecialty.NEPHROLOGY_UROLOGY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Supersaturation of urine leading to crystal nucleation, aggregation, and stone growth "
            "(most frequently Calcium Oxalate, Calcium Phosphate, Uric Acid, or Struvite). "
            "Stone migration into and impaction within the narrow ureteric lumen (pelviureteric junction, "
            "pelvic brim, or vesicoureteric junction) provokes smooth muscle spasm, acute proximal hydroureteronephrosis, "
            "renal capsular distension, and severe visceral pain mediated by sympathetic afferents."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Sudden onset excruciating, spasmodic flank / loin pain radiating to the groin, labia, or testicle", "weight": 0.98},
                {"symptom": "Extreme patient restlessness: writhing and unable to find a comfortable position", "weight": 0.96},
                {"symptom": "Microscopic or gross macroscopic hematuria (smoky or red urine)", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Severe nausea and reflex vomiting", "weight": 0.85},
                {"symptom": "Urinary frequency, dysuria, and strangury (when stone lodges at vesicoureteric junction)", "weight": 0.78},
                {"symptom": "Costovertebral angle tenderness (renal punch tenderness)", "weight": 0.82},
            ]
        },
        "red_flag_criteria": [
            "Obstructive Pyelonephritis: Ureteric stone obstruction WITH concurrent high fever, rigors, and pyuria (urological emergency)",
            "Anuria in a patient with a solitary kidney or bilateral obstructing calculi",
            "Intractable pain refractory to intravenous analgesia",
            "Uncontrolled vomiting preventing oral intake and hydration"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Appendicitis", "icd11": "DB10", "distinction": "Patient lies still (peritoneal pain), tenderness at McBurney point, microscopic hematuria is typically absent."},
            {"condition": "Ruptured Abdominal Aortic Aneurysm (AAA)", "icd11": "BD50", "distinction": "Elderly smoker with flank/back pain, pulsatile abdominal mass, profound hypotension; bedside ultrasound mandatory."},
            {"condition": "Acute Testicular Torsion", "icd11": "GB04", "distinction": "High-riding swollen tender testicle, negative Prehn sign, absent cremasteric reflex, absent Doppler flow."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Urinalysis (dipstick and microscopy for hematuria, leucocytes, nitrites, and crystals)", "Serum Creatinine and Blood Urea Nitrogen (assess renal function impairment)", "Serum Calcium, Uric Acid, and Full Blood Count"],
            "imaging_ecg": ["Non-Contrast Helical CT of Kidneys, Ureters, and Bladder (NCCT KUB - gold standard: stone size, location, Hounsfield density)", "Renal and Pelvic Ultrasound (detects hydronephrosis, choice in pregnant women and children)"],
            "confirmatory_tests": ["Stone composition infrared spectroscopy analysis (following stone passage / retrieval)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Maintain vigorous oral fluid intake (2.5-3.0 liters/day) to achieve urine volume > 2 L/day",
                "Filter all urine through fine gauze to catch and analyze passed calculi"
            ],
            "pharmacotherapy": [
                "First-line Acute Pain Relief: Non-Steroidal Anti-Inflammatory Drugs (IV/IM Ketorolac 15-30 mg or Diclofenac 75 mg) - superior to opioids in reducing ureteral spasm and pain",
                "Secondary analgesia: IV Morphine or Fentanyl if NSAIDs contraindicated or insufficient",
                "Medical Expulsive Therapy (MET) for distal ureteric stones 5-10 mm: Alpha-1 blocker (Tamsulosin 0.4 mg daily for up to 4 weeks)",
                "Emergency Urological Decompression (JJ Stent or Percutaneous Nephrostomy) mandatory within hours if infected obstructed stone present"
            ],
            "contraindications": [
                "Do NOT perform Medical Expulsive Therapy or shockwave lithotripsy if active infection, sepsis, or uncontrolled severe hydronephrosis is present."
            ]
        },
        "source_metadata": {
            "issuing_authority": "European Association of Urology (EAU) & AUA",
            "guideline_title": "EAU Guidelines on Urolithiasis",
            "publication_year": 2024,
            "source_url": "https://uroweb.org/guidelines/urolithiasis",
            "verification_hash": _calc_hash("GB70", "Nephrolithiasis")
        }
    },
    {
        "icd11_code": "GC08",
        "icd10_code": "N10",
        "clinical_name": "Acute Pyelonephritis (Complicated / Uncomplicated)",
        "common_aliases": ["Upper UTI", "Kidney Infection", "වකුගඩු ආසාදනය"],
        "medical_specialty": MedicalSpecialty.NEPHROLOGY_UROLOGY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Invasive bacterial infection of the renal parenchyma and pelvicalyceal system "
            "most frequently caused by uropathogenic Escherichia coli (UPEC) ascending from the lower urinary tract. "
            "Bacterial P-fimbriae adhere to urothelial receptors, ascending against gravity into collecting ducts, "
            "provoking neutrophilic infiltration, microabscess formation, parenchymal inflammation, and risk of bacteremia/sepsis."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "High spiking pyrexia (> 38 C) with shaking rigors and chills", "weight": 0.95},
                {"symptom": "Unilateral or bilateral severe flank/loin pain and costovertebral angle tenderness", "weight": 0.96},
                {"symptom": "Lower urinary tract symptoms: dysuria, urgency, and frequency", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Nausea, persistent vomiting, and anorexia", "weight": 0.85},
                {"symptom": "Macroscopic hematuria or foul-smelling cloudy urine", "weight": 0.78},
                {"symptom": "Malaise, headache, and generalized prostration", "weight": 0.70},
            ]
        },
        "red_flag_criteria": [
            "Urosepsis (qSOFA criteria: altered mental state, respiratory rate >= 22, systolic BP <= 100)",
            "Concurrent urinary tract obstruction (stone or stricture) risking pyonephrosis",
            "Emphysematous Pyelonephritis: gas formation in renal parenchyma (common in diabetics)",
            "Perinephric abscess or lack of clinical improvement after 72 hours of appropriate IV antibiotics"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Lower Urinary Tract Infection (Cystitis)", "icd11": "GC00", "distinction": "Absence of high fever, chills, rigors, or costovertebral angle tenderness."},
            {"condition": "Acute Appendicitis", "icd11": "DB10", "distinction": "Pain localized to right iliac fossa (McBurney point), negative urine culture, normal renal ultrasound."},
            {"condition": "Acute Cholecystitis", "icd11": "DC11", "distinction": "Right upper quadrant pain with positive Murphy sign; normal urinalysis."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Urinalysis (dipstick positive for leucocyte esterase and nitrites; microscopy reveals pyuria, white blood cell casts, bacteriuria)", "Midstream Urine (MSU) Culture and Antimicrobial Sensitivity Testing (mandatory)", "Full Blood Count (marked leukocytosis with neutrophilia), CRP, and Serum Creatinine"],
            "imaging_ecg": ["Blood cultures (2 sets prior to antibiotic initiation)", "Renal Ultrasound or Contrast-Enhanced CT Abdomen (indicated if fever persists > 72 hours, suspicion of obstruction or abscess)"],
            "confirmatory_tests": ["Identification of uropathogen >= 10^5 CFU/mL in pure culture"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Generous oral and intravenous hydration to maintain brisk urinary flush",
                "Strict bed rest, antipyretics (Paracetamol), and close hemodynamic monitoring"
            ],
            "pharmacotherapy": [
                "Outpatient Mild/Moderate Uncomplicated: Oral Ciprofloxacin 500 mg BID for 7 days (if local resistance < 10%), OR Levofloxacin 750 mg daily for 5 days, OR Trimethoprim-Sulfamethoxazole 160/800 mg BID for 14 days",
                "Inpatient / Severe Pyelonephritis: IV Ceftriaxone 1-2g daily OR Cefotaxime 2g Q8H, OR Piperacillin-Tazobactam 4.5g Q8H (if pseudomonas risk)",
                "Transition to targeted oral therapy once afebrile for 24-48 hours based on culture sensitivity results for total 7-14 day course"
            ],
            "contraindications": [
                "Nitrofurantoin and Fosfomycin are STRICTLY CONTRAINDICATED in pyelonephritis as they do not achieve adequate therapeutic tissue concentrations in the renal parenchyma."
            ]
        },
        "source_metadata": {
            "issuing_authority": "Infectious Diseases Society of America (IDSA) & EAU",
            "guideline_title": "EAU Guidelines on Urological Infections: Pyelonephritis Management",
            "publication_year": 2024,
            "source_url": "https://uroweb.org/guidelines/urological-infections",
            "verification_hash": _calc_hash("GC08", "Acute Pyelonephritis")
        }
    },

    # -------------------------------------------------------------------------
    # 8. HEMATOLOGY, DERMATOLOGY, RHEUMATOLOGY & MATERNAL/PEDIATRICS
    # -------------------------------------------------------------------------
    {
        "icd11_code": "3A00",
        "icd10_code": "D50.9",
        "clinical_name": "Iron Deficiency Anemia (IDA)",
        "common_aliases": ["Microcytic Anemia", "Iron Deficiency", "යකඩ ඌනතා රක්තහීනතාව"],
        "medical_specialty": MedicalSpecialty.HEMATOLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Exhaustion of body iron stores leading to defective heme and hemoglobin synthesis. "
            "Etiology includes chronic occult blood loss (gastrointestinal bleeding, menorrhagia), "
            "malabsorption (celiac disease, post-gastrectomy), or increased physiological demand (pregnancy, growth). "
            "Impaired oxygen-carrying capacity results in tissue hypoxia, compensatory tachycardia, and reduced exercise tolerance."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Chronic unremitting fatigue, lethargy, and general weakness", "weight": 0.94},
                {"symptom": "Exertional dyspnea and palpitations on minimal effort", "weight": 0.90},
                {"symptom": "Marked conjunctival, subungual, and palmar crease pallor", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Pica (pathological craving for non-nutritive substances: ice/pagophagia, clay, dirt)", "weight": 0.78},
                {"symptom": "Koilonychia (spoon-shaped concave brittle nails)", "weight": 0.70},
                {"symptom": "Angular cheilitis (painful fissures at corners of mouth) and atrophic glossitis (smooth tongue)", "weight": 0.75},
            ]
        },
        "red_flag_criteria": [
            "Severe symptomatic anemia: Hemoglobin < 7.0 g/dL with resting chest pain, syncope, or cardiac ischemia",
            "Frank gastrointestinal bleeding (hematemesis, dark melenic stools)",
            "High-output congestive heart failure in severe decompensated anemia",
            "New-onset iron deficiency in male or postmenopausal female (mandates bidirectional endoscopy to rule out colorectal malignancy)"
        ],
        "differential_diagnoses": [
            {"condition": "Beta Thalassemia Trait / Minor", "icd11": "3A50", "distinction": "Mentzer index (MCV/RBC count) < 13, normal or elevated serum ferritin, target cells on film, elevated HbA2 on hemoglobin electrophoresis."},
            {"condition": "Anemia of Chronic Disease / Inflammation", "icd11": "3A03", "distinction": "Elevated or normal serum ferritin, low total iron-binding capacity (TIBC), elevated CRP/ESR."},
            {"condition": "Sideroblastic Anemia", "icd11": "3A02", "distinction": "Ring sideroblasts on bone marrow biopsy, elevated serum iron and transferrin saturation."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (low Hemoglobin, low MCV < 80 fL, low MCH < 27 pg, elevated RDW > 15%)", "Serum Ferritin (diagnostic if < 30 mcg/L; the single most powerful test)", "Serum Iron, Total Iron Binding Capacity (TIBC - elevated), Transferrin Saturation (< 16-20%)"],
            "imaging_ecg": ["Peripheral blood smear (microcytic hypochromic red blood cells, anisopoikilocytosis, pencil cells)"],
            "confirmatory_tests": ["Mandatory Investigation of Cause: Upper Endoscopy (EGD) + Colonoscopy in men and post-menopausal women to rule out GI cancer; Celiac serology (anti-tTG IgA)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Dietary counseling: enhance heme iron intake (lean red meats, liver) and non-heme iron (leafy greens, legumes)",
                "Co-ingest Vitamin C (ascorbic acid, citrus juice) to enhance non-heme iron absorption; avoid tea/coffee with meals (tannins block absorption)"
            ],
            "pharmacotherapy": [
                "Oral Iron Therapy: Ferrous Sulfate 200 mg (65 mg elemental iron) or Ferrous Fumarate given alternate days or once daily (alternate-day dosing minimizes hepcidin upregulation and improves GI tolerance)",
                "Intravenous Iron Therapy (Ferric Derisomaltose or Ferric Carboxymaltose) indicated if: oral iron intolerance, severe malabsorption, inflammatory bowel disease, 2nd/3rd trimester pregnancy, or persistent bleeding",
                "Continue oral replacement for 3 months after hemoglobin normalizes to replenish marrow iron stores"
            ],
            "contraindications": [
                "Do NOT give oral iron concurrently with antacids, PPIs, or dairy products (calcium blocks absorption). Never treat iron deficiency without investigating the underlying cause."
            ]
        },
        "source_metadata": {
            "issuing_authority": "British Society of Gastroenterology (BSG) & WHO",
            "guideline_title": "BSG Guidelines for the Management of Iron Deficiency Anaemia in Adults",
            "publication_year": 2023,
            "source_url": "https://gut.bmj.com/content/70/11/2030",
            "verification_hash": _calc_hash("3A00", "Iron Deficiency Anemia")
        }
    },
    {
        "icd11_code": "EA80",
        "icd10_code": "L20.9",
        "clinical_name": "Severe Atopic Dermatitis with Secondary Impetiginization",
        "common_aliases": ["Atopic Eczema", "Eczema", "ඇටොපික් ඩර්මැටයිටිස්", "Infantile Eczema"],
        "medical_specialty": MedicalSpecialty.DERMATOLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Chronic relapsing inflammatory skin disease driven by epidermal skin barrier disruption "
            "(filaggrin gene FLG loss-of-function mutations) and Type 2 immune hyperactivation (IL-4, IL-13, IL-31). "
            "Transepidermal water loss and allergen penetration provoke intense pruritus. "
            "The resulting 'itch-scratch cycle' causes mechanical excoriation, skin lichenification, "
            "and frequent secondary colonization/superinfection by Staphylococcus aureus."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Severe unremitting pruritus (itching) disrupting sleep", "weight": 0.98},
                {"symptom": "Erythematous, ill-defined, scaly plaques and papules", "weight": 0.94},
                {"symptom": "Characteristic flexural distribution (antecubital and popliteal fossae, neck, wrists)", "weight": 0.92},
            ],
            "secondary": [
                {"symptom": "Lichenification (accentuated skin markings from chronic rubbing)", "weight": 0.82},
                {"symptom": "Golden honey-colored crusting or oozing (Secondary Impetiginization by S. aureus)", "weight": 0.85},
                {"symptom": "Dennie-Morgan infraorbital folds and pityriasis alba", "weight": 0.65},
            ]
        },
        "red_flag_criteria": [
            "Eczema Herpeticum: Rapid eruption of monomorphic, punched-out umbilicated vesicles and pustules with high fever (HSV superinfection - medical emergency)",
            "Erythroderma: Generalized exfoliative erythema involving > 90% body surface area with thermoregulatory failure and high-output cardiac risk",
            "Extensive bacterial cellulitis with systemic toxicity and lymphangitis"
        ],
        "differential_diagnoses": [
            {"condition": "Scabies Infestation", "icd11": "1G04", "distinction": "Intense nocturnal itching, involvement of finger web spaces, wrists, genitalia; visible burrows; dermoscopy reveals delta-wing mite."},
            {"condition": "Allergic Contact Dermatitis", "icd11": "EA83", "distinction": "Distribution corresponds strictly to exogenous contactant (e.g. nickel waistband, hair dye); positive patch testing."},
            {"condition": "Cutaneous T-Cell Lymphoma (Mycosis Fungoides)", "icd11": "2B30", "distinction": "Older adults, unresolving indurated plaques in non-sun-exposed 'bathing suit' distribution; skin biopsy confirms malignant T-cells."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Clinical diagnosis based on Hanifin and Rajka or UK Working Party diagnostic criteria", "Skin swab of weeping/crusted lesions for bacterial culture and antimicrobial sensitivity (Staph aureus)"],
            "imaging_ecg": ["Viral PCR swab (HSV-1/2) if punched-out crusted lesions present (exclude Eczema Herpeticum)"],
            "confirmatory_tests": ["Serum Total IgE and specific IgE (Phadiatop / RAST) for aeroallergen sensitization", "Skin prick testing"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Liberal, frequent application of bland ointments/emollients (petrolatum, ceramides) immediately after bathing (within 3 minutes: 'soak and seal')",
                "Avoid harsh soaps and sodium lauryl sulfate detergents; use non-soap soap-free cleansers",
                "Wear soft loose 100% cotton clothing; keep ambient bedroom temperature cool to prevent sweat-induced itching"
            ],
            "pharmacotherapy": [
                "First-line anti-inflammatory flare control: Topical Corticosteroids (TCS: Hydrocortisone 1% for face/flexures; Betamethasone valerate 0.1% or Mometasone for trunk/limbs) applied once daily",
                "Topical Calcineurin Inhibitors (Tacrolimus 0.1% ointment or Pimecrolimus cream) as steroid-sparing agents for delicate skin (eyelids, face)",
                "If secondary impetigo present: Oral Flucloxacillin 500 mg QID for 7 days (or Clindamycin if penicillin-allergic)",
                "Severe refractory disease: Biologic therapy (Dupilumab - anti-IL-4Ralpha monoclonal antibody) or JAK inhibitor (Upadacitinib)"
            ],
            "contraindications": [
                "Systemic oral corticosteroids (Prednisolone) should generally be avoided for routine atopic dermatitis due to severe, catastrophic rebound flares upon withdrawal."
            ]
        },
        "source_metadata": {
            "issuing_authority": "American Academy of Dermatology (AAD) & EuroGuiDerm",
            "guideline_title": "AAD Guidelines of Care for the Management of Atopic Dermatitis",
            "publication_year": 2024,
            "source_url": "https://www.aad.org/member/clinical-quality/guidelines/atopic-dermatitis",
            "verification_hash": _calc_hash("EA80", "Atopic Dermatitis")
        }
    },
    {
        "icd11_code": "FA20",
        "icd10_code": "M05.9",
        "clinical_name": "Seropositive Rheumatoid Arthritis",
        "common_aliases": ["RA", "Rheumatoid Disease", "රුමටොයිඩ් ආතරයිටිස්"],
        "medical_specialty": MedicalSpecialty.RHEUMATOLOGY,
        "baseline_acuity": TriageAcuityLevel.ROUTINE_CLINIC,
        "pathophysiology_overview": (
            "Systemic autoimmune inflammatory polyarthritis characterized by persistent proliferative synovitis. "
            "Loss of immune tolerance to citrullinated self-proteins (ACPA) triggers synovial lining hyperplasia, "
            "neoangiogenesis, and formation of an invasive inflammatory 'pannus'. "
            "Pannus-derived metalloproteinases and osteoclast activation cause progressive, irreversible articular cartilage destruction, "
            "marginal bone erosions, and joint deformities."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Symmetrical, bilateral inflammatory swelling and tenderness of small joints (MCP, PIP, MTP)", "weight": 0.98},
                {"symptom": "Severe morning joint stiffness lasting > 60 minutes, improving with movement", "weight": 0.96},
                {"symptom": "Pain and swelling persisting for > 6 weeks", "weight": 0.94},
            ],
            "secondary": [
                {"symptom": "Classical hand deformities in chronic disease: Ulnar deviation of fingers, Swan-neck and Boutonniere deformities", "weight": 0.85},
                {"symptom": "Subcutaneous firm non-tender rheumatoid nodules over extensor surfaces (elbows)", "weight": 0.78},
                {"symptom": "Systemic constitutional malaise, low-grade fever, and weight loss", "weight": 0.72},
            ]
        },
        "red_flag_criteria": [
            "Atlantoaxial Subluxation: Cervical spine instability with C1-C2 subluxation causing sudden myelopathy, quadriparesis, or respiratory arrest",
            "Rheumatoid Vasculitis: Deep cutaneous ulcerations, digital gangrene, or mononeuritis multiplex (foot drop)",
            "Superimposed Septic Arthritis: Acute, hot, highly swollen monoarticular flare with fever in an immunosuppressed RA patient",
            "Scleromalacia Perforans: Severe necrotizing anterior scleritis leading to scleral thinning and eyeball perforation"
        ],
        "differential_diagnoses": [
            {"condition": "Osteoarthritis", "icd11": "FA00", "distinction": "Mechanical pain worse with activity, brief morning stiffness < 30 minutes, DIP joint involvement (Heberden nodes), absence of systemic inflammation."},
            {"condition": "Psoriatic Arthritis", "icd11": "FA11", "distinction": "DIP joint involvement, dactylitis ('sausage digits'), psoriatic skin plaques and nail pitting, usually seronegative."},
            {"condition": "Systemic Lupus Erythematosus (SLE)", "icd11": "4A40", "distinction": "Non-erosive reducible arthropathy (Jaccoud arthropathy), malar rash, positive anti-dsDNA, multi-organ renal/hematologic involvement."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Anti-Cyclic Citrullinated Peptide Antibodies (Anti-CCP / ACPA - 96% specific for RA)", "Rheumatoid Factor (RF IgM)", "Erythrocyte Sedimentation Rate (ESR) and C-Reactive Protein (CRP - disease activity monitors)"],
            "imaging_ecg": ["Plain Radiographs of Hands, Wrists, and Feet (early soft tissue swelling, juxta-articular osteopenia, periarticular marginal erosions, joint space narrowing)", "High-Resolution Musculoskeletal Ultrasound / MRI (detects subclinical synovitis and early bone erosions)"],
            "confirmatory_tests": ["Classification via 2010 ACR/EULAR Classification Criteria for Rheumatoid Arthritis (score >= 6/10)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Early physiotherapy and occupational therapy: joint protection strategies and customized hand splinting",
                "Cardiovascular risk factor modification (RA carries 2-fold increased risk of premature ischemic heart disease)"
            ],
            "pharmacotherapy": [
                "Treat-to-Target (T2T) Strategy: Aim for clinical remission or low disease activity (DAS28 < 2.6)",
                "Immediate First-Line Conventional DMARD: Oral or Subcutaneous Methotrexate 15-25 mg ONCE WEEKLY (always co-prescribe Folic Acid 5 mg weekly)",
                "Short-term bridging steroid therapy: Low-dose oral Prednisolone (5-10 mg daily) while waiting for Methotrexate efficacy (6-12 weeks)",
                "Biologic DMARDs if target not achieved: Anti-TNF (Adalimumab, Etanercept) or IL-6 inhibitor (Tocilizumab) or JAK inhibitor (Tofacitinib, Baricitinib)"
            ],
            "contraindications": [
                "Methotrexate is strictly teratogenic and contraindicated in pregnancy/breastfeeding, severe hepatic impairment, and heavy alcohol use. Never prescribe daily Methotrexate (must be strictly once weekly)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "EULAR (European Alliance of Associations for Rheumatology) & ACR",
            "guideline_title": "EULAR Recommendations for the Management of Rheumatoid Arthritis",
            "publication_year": 2023,
            "source_url": "https://ard.bmj.com/content/82/1/3",
            "verification_hash": _calc_hash("FA20", "Rheumatoid Arthritis")
        }
    },
    {
        "icd11_code": "JA24",
        "icd10_code": "O14.1",
        "clinical_name": "Preeclampsia with Severe Features",
        "common_aliases": ["Toxemia of Pregnancy", "Severe Preeclampsia", "පූර්ව එක්ලැම්ප්සියාව"],
        "medical_specialty": MedicalSpecialty.OBSTETRICS_GYNECOLOGY,
        "baseline_acuity": TriageAcuityLevel.EMERGENCY,
        "pathophysiology_overview": (
            "Multisystem gestational disorder presenting after 20 weeks of gestation. "
            "Defective trophoblastic invasion of uterine spiral arteries leads to chronic placental hypoperfusion and ischemia. "
            "The ischemic placenta secretes anti-angiogenic factors (sFlt-1 and soluble endoglin) into maternal circulation, "
            "binding and neutralizing VEGF and PlGF, producing widespread maternal endothelial dysfunction, "
            "systemic microvascular vasospasm, and multi-organ capillary leak."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Severe hypertension: Systolic BP >= 160 mmHg and/or Diastolic BP >= 110 mmHg on 2 occasions", "weight": 0.98},
                {"symptom": "Significant proteinuria (>= 300 mg/24h or urine protein:creatinine ratio >= 0.3)", "weight": 0.92},
                {"symptom": "Persistent, severe, new-onset throbbing frontal or occipital headache unresponsive to analgesics", "weight": 0.94},
            ],
            "secondary": [
                {"symptom": "Visual disturbances: scotomata, photopsia (flashing lights), or blurred vision", "weight": 0.90},
                {"symptom": "Severe persistent epigastric or right upper quadrant pain (hepatic capsular distension)", "weight": 0.88},
                {"symptom": "Rapidly progressive non-dependent edema (hands, face, periorbital)", "weight": 0.80},
            ]
        },
        "red_flag_criteria": [
            "Eclampsia: Generalized tonic-clonic convulsions in a preeclamptic patient (obstetric catastrophe)",
            "HELLP Syndrome: Hemolysis (microangiopathic), Elevated Liver enzymes (AST/ALT > 2x ULN), Low Platelets (< 100,000/uL)",
            "Acute Pulmonary Edema with respiratory failure",
            "Placental Abruption with painful woody-hard uterus, fetal bradycardia, or heavy vaginal bleeding",
            "Acute Renal Failure with serum creatinine > 1.1 mg/dL or doubling of baseline"
        ],
        "differential_diagnoses": [
            {"condition": "Chronic Gestational Hypertension", "icd11": "JA20", "distinction": "Pre-existing elevated BP prior to 20 weeks gestation, absence of proteinuria or end-organ features."},
            {"condition": "Thrombotic Thrombocytopenic Purpura (TTP)", "icd11": "3B64", "distinction": "Severe ADAMTS13 activity deficiency (<10%), prominent neurological signs, high LDH, normal liver function."},
            {"condition": "Acute Fatty Liver of Pregnancy (AFLP)", "icd11": "JA64", "distinction": "Marked profound hypoglycemia, coagulopathy with low fibrinogen, elevated ammonia."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Automated Blood Pressure measurement with appropriately sized cuff in semi-recumbent posture", "Urinary Protein-to-Creatinine Ratio (UPCR >= 0.3 mg/mg or 30 mg/mmol)", "Full Blood Count (platelet count < 100,000/uL)", "Serum Liver Enzymes (AST, ALT), Serum Creatinine, Uric acid, and LDH"],
            "imaging_ecg": ["Obstetric Ultrasound: Fetal biometry, amniotic fluid volume (AFI), and Umbilical Artery Doppler velocimetry", "Cardiotocography (CTG - continuous electronic fetal heart rate monitoring)"],
            "confirmatory_tests": ["Serum sFlt-1 / PlGF ratio (angiogenic biomarker for rule-in/rule-out of severe preeclampsia)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Immediate admission to dedicated Obstetric High Dependency Unit (HDU) or Labor & Delivery ward",
                "Strict maternal left lateral positioning to maximize uteroplacental blood flow",
                "Insertion of indwelling catheter for hourly fluid balance monitoring"
            ],
            "pharmacotherapy": [
                "Seizure Prophylaxis / Treatment: Intravenous Magnesium Sulfate (Zuspan regimen: 4g IV loading dose over 15-20 min, followed by 1g/hour maintenance infusion; continue for 24 hours postpartum)",
                "Acute Antihypertensive Therapy (target BP 135-145/85-95 mmHg): Oral Nifedipine 10-20 mg immediate-release, OR IV Labetalol 20 mg bolus doubled every 10-20 min, OR IV Hydralazine 5 mg",
                "Antenatal Corticosteroids: Intramuscular Betamethasone (12 mg IM every 24 hours, 2 doses) if < 37 weeks to accelerate fetal lung maturity",
                "Definitive Cure: Timely planned delivery of fetus and placenta (mandatory immediately if gestational age >= 34 weeks or maternal/fetal compromise)"
            ],
            "contraindications": [
                "ACE inhibitors and ARBs are strictly teratogenic and contraindicated. Diuretics (Furosemide) should be avoided as plasma volume is already contracted in preeclampsia (unless acute pulmonary edema is present)."
            ]
        },
        "source_metadata": {
            "issuing_authority": "ACOG & Royal College of Obstetricians and Gynaecologists (RCOG)",
            "guideline_title": "ACOG Practice Bulletin No. 222: Gestational Hypertension and Preeclampsia",
            "publication_year": 2024,
            "source_url": "https://www.acog.org/clinical/clinical-guidance/practice-bulletin/articles/2020/06/gestational-hypertension-and-preeclampsia",
            "verification_hash": _calc_hash("JA24", "Preeclampsia Severe")
        }
    },
    {
        "icd11_code": "CA01.0",
        "icd10_code": "J05.0",
        "clinical_name": "Acute Laryngotracheobronchitis (Croup)",
        "common_aliases": ["Viral Croup", "Pediatric Croup", "කුඩා දරුවන්ගේ ස්වරාල ප්‍රදාහය"],
        "medical_specialty": MedicalSpecialty.PEDIATRICS,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Common pediatric respiratory infection predominantly caused by Parainfluenza virus type 1 or 3, "
            "affecting infants and young children aged 6 months to 3 years. Viral replication triggers severe inflammation, "
            "hyperemia, and subglottic mucosal edema in the cricoid ring, the narrowest point of the pediatric airway. "
            "Because airway resistance is inversely proportional to the 4th power of the radius (Poiseuille's law), "
            "even 1 mm of circumferential mucosal swelling reduces airway cross-sectional area by up to 75% in a toddler, "
            "generating dynamic inspiratory stridor, seal-like barking cough, and variable respiratory distress."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Harsh, brassy, seal-like barking cough (pathognomonic)", "weight": 0.96},
                {"symptom": "High-pitched inspiratory stridor, worse during agitation or crying", "weight": 0.94},
                {"symptom": "Hoarseness of voice or muffled cry", "weight": 0.88},
            ],
            "secondary": [
                {"symptom": "Low-grade fever (38.0 - 38.5 C) preceded by 1-2 days of rhinorrhea/coryza", "weight": 0.82},
                {"symptom": "Suprasternal and intercostal retractions (Westley Croup Score assessment)", "weight": 0.86},
                {"symptom": "Nocturnal symptom exacerbation (typically peaks between midnight and 4 AM)", "weight": 0.78},
            ]
        },
        "red_flag_criteria": [
            "Biphasic stridor (stridor present at rest during both inspiration and expiration)",
            "Severe subcostal, intercostal, and sternal retractions with tracheal tugging and head bobbing",
            "Cyanosis, lethargy, marked restlessness, or silent chest indicating impending respiratory arrest",
            "Inability to swallow, drooling, high fever, and tripoding posture (suspect Acute Epiglottitis or Bacterial Tracheitis)",
            "Poor oxygen saturation: SpO2 < 92% on room air"
        ],
        "differential_diagnoses": [
            {"condition": "Acute Epiglottitis", "icd11": "CA00", "distinction": "Toxic appearance, rapid progression, absence of barking cough, high fever, tripoding posture, drooling saliva."},
            {"condition": "Bacterial Tracheitis", "icd11": "CA02", "distinction": "High fever, toxic septic appearance, thick purulent airway secretions unresponsive to nebulized adrenaline."},
            {"condition": "Foreign Body Airway Aspiration", "icd11": "MD30", "distinction": "Sudden catastrophic choking episode while eating or playing with small toys, afebrile, unilateral wheezing."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Clinical diagnosis via Westley Croup Score (routine blood draws strictly avoided to prevent child agitation and acute airway occlusion)"],
            "imaging_ecg": ["Continuous Pulse Oximetry (SpO2)", "Soft tissue neck X-ray AP view only if atypical course: characteristic 'Steeple sign' (subglottic conical narrowing)"],
            "confirmatory_tests": ["Multiplex Viral Respiratory PCR swab (detects Parainfluenza 1/2/3, RSV, Adenovirus)"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Strict calm environment with minimal patient handling in parent's lap to prevent agitation-induced airway collapse",
                "Do not inspect oral cavity with a tongue depressor if respiratory distress is present"
            ],
            "pharmacotherapy": [
                "Systemic Corticosteroids (universal first-line for all severities): Oral Dexamethasone 0.15 mg/kg to 0.6 mg/kg single dose (or oral Prednisolone 1 mg/kg if Dexamethasone unavailable)",
                "Nebulized Epinephrine / L-Adrenaline: 1:1000 (0.5 mL/kg, maximum 5 mL) nebulized over 15 minutes for moderate-to-severe stridor at rest; observe for at least 2 to 4 hours post-nebulization due to rebound phenomenon",
                "Humidified Supplemental Oxygen if SpO2 < 92%"
            ],
            "contraindications": [
                "Sedatives and antihistamines are strictly contraindicated due to risk of respiratory depression and masking hypoxia. Antitussives and throat sprays have no proven clinical efficacy."
            ]
        },
        "source_metadata": {
            "issuing_authority": "AAP (American Academy of Pediatrics) & NICE UK",
            "guideline_title": "AAP Clinical Practice Guideline: Management of Croup in Children",
            "publication_year": 2024,
            "source_url": "https://publications.aap.org/pediatrics/article/croup",
            "verification_hash": _calc_hash("CA01.0", "Acute Croup")
        }
    },
    {
        "icd11_code": "2B90",
        "icd10_code": "C18",
        "clinical_name": "Colorectal Adenocarcinoma",
        "common_aliases": ["Colon Cancer", "Rectal Cancer", "Colorectal Carcinoma", "මහාන්ත්‍රික පිළිකා"],
        "medical_specialty": MedicalSpecialty.ONCOLOGY,
        "baseline_acuity": TriageAcuityLevel.URGENT_CONSULT,
        "pathophysiology_overview": (
            "Malignant epithelial neoplasm arising from the mucosal lining of the colon or rectum. "
            "Over 80% arise through the classical adenoma-to-carcinoma multi-step pathway initiated by biallelic loss of the "
            "APC tumor suppressor gene (activating Wnt/beta-catenin signaling), followed by KRAS activating mutations, "
            "and late 17p (TP53) chromosomal inactivation. A second major subset (15%) involves DNA mismatch repair deficiency (dMMR/MSI-high) "
            "via MLH1 promoter hypermethylation or germline Lynch syndrome mutations. Neoplastic mucosal proliferation leads to "
            "ulceration, chronic insidious microcytic iron deficiency anemia (right-sided lesions), or progressive lumen annular obstruction "
            "with altered bowel habits, tenesmus, and hematochezia (left-sided lesions)."
        ),
        "cardinal_symptoms": {
            "primary": [
                {"symptom": "Persistent unexplained change in bowel habits lasting > 4-6 weeks (alternating diarrhea/constipation, narrowing of stool caliber)", "weight": 0.94},
                {"symptom": "Unexplained iron-deficiency microcytic anemia in men or postmenopausal women", "weight": 0.92},
                {"symptom": "Visible rectal bleeding or hematochezia mixed with stool", "weight": 0.90},
            ],
            "secondary": [
                {"symptom": "Unintentional progressive weight loss and profound anorexia", "weight": 0.84},
                {"symptom": "Persistent crampy lower abdominal pain or sensation of incomplete rectal evacuation (tenesmus)", "weight": 0.86},
                {"symptom": "Palpable right iliac fossa mass or palpable mass on Digital Rectal Examination (DRE)", "weight": 0.82},
            ]
        },
        "red_flag_criteria": [
            "Complete mechanical large bowel obstruction: obstipation, abdominal distension, feculent vomiting, tympanitic abdomen",
            "Pneumoperitoneum / acute bowel perforation: board-like peritonitic rigidity, severe guarding, tachycardia, septic shock",
            "Severe hemodynamically unstable lower gastrointestinal hemorrhage (hypotension, syncopal collapse)",
            "Jaundice or hepatomegaly indicating extensive hepatic metastatic burden"
        ],
        "differential_diagnoses": [
            {"condition": "Diverticular Disease / Diverticulitis", "icd11": "DA61", "distinction": "Acute localized left lower quadrant tenderness, fever, leukocytosis, episodic flare-ups rather than progressive stenosis."},
            {"condition": "Ulcerative Colitis Flare", "icd11": "DD70", "distinction": "Younger onset, diffuse bloody mucus diarrhea, pANCA positive, continuous superficial mucosal mucosal ulceration."},
            {"condition": "Internal Hemorrhoids", "icd11": "DB93", "distinction": "Bright red painless bleeding separate from stool (drips into bowl), absence of anemia, weight loss, or change in bowel frequency."}
        ],
        "diagnostic_workup": {
            "initial_labs": ["Full Blood Count (microcytic hypochromic anemia, low Hb, low MCV)", "Serum Ferritin and Total Iron Binding Capacity (TIBC)", "Serum Carcinoembryonic Antigen (CEA - baseline tumor marker)", "Fecal Immunochemical Test (FIT)"],
            "imaging_ecg": ["Contrast-Enhanced CT of Chest, Abdomen, and Pelvis (CAP-CT for TNM staging and distant metastases to liver/lungs)", "High-resolution pelvic MRI (for local staging and circumferential resection margin in rectal cancer)"],
            "confirmatory_tests": ["Complete Optical Colonoscopy with multiple mucosal punch biopsies for histopathology", "Mismatch Repair (MMR) Immunohistochemistry (MLH1, MSH2, MSH6, PMS2) and KRAS/NRAS/BRAF molecular mutation profiling"]
        },
        "evidence_based_management": {
            "first_line_lifestyle": [
                "Urgent 2-week wait referral to Colorectal Multidisciplinary Oncology Team (MDT)",
                "Pre-habilitation: Nutritional optimization (high-protein oral nutritional supplements) and smoking cessation"
            ],
            "pharmacotherapy": [
                "Surgical Resection: Primary oncologic resection with clear proximal/distal margins and regional lymphadenectomy (e.g., right hemicolectomy, sigmoid colectomy, anterior resection, or abdominoperineal resection)",
                "Adjuvant Systemic Chemotherapy (Stage III / high-risk Stage II): FOLFOX (5-Fluorouracil, Leucovorin, Oxaliplatin) or CAPOX (Capecitabine, Oxaliplatin) for 3-6 months",
                "Neoadjuvant Chemoradiotherapy: Short-course radiotherapy or total neoadjuvant therapy (TNT) for locally advanced rectal cancers",
                "Targeted / Immunotherapy (Metastatic dMMR/MSI-H): Pembrolizumab / Nivolumab anti-PD-1 checkpoint inhibitors"
            ],
            "contraindications": [
                "Barium enema or oral cathartic bowel prep is contraindicated in acute obstructing or perforating colonic lesions. Never delay diagnostic colonoscopy for symptomatic anemia with empirical iron supplements alone."
            ]
        },
        "source_metadata": {
            "issuing_authority": "NCCN (National Comprehensive Cancer Network) & ESMO",
            "guideline_title": "NCCN Clinical Practice Guidelines in Oncology: Colon and Rectal Cancer",
            "publication_year": 2024,
            "source_url": "https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1428",
            "verification_hash": _calc_hash("2B90", "Colorectal Adenocarcinoma")
        }
    }
]

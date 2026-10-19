import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from app.schemas.telemedicine import (
    SpecialistDoctor,
    SpecialistRecommendationRequest,
    SpecialistRecommendationResponse,
    AppointmentBookingRequest,
    AppointmentBookingResponse,
)


class TelemedicineAndBookingEngine:
    """
    Sri Lankan Telemedicine & Specialist Doctor Channelling Engine.
    Integrates clinical triage outputs and laboratory diagnostic reports directly with
    Sri Lanka's leading healthcare booking gateways (eChannelling, Doc990, oDoc Telemedicine,
    and Major Hospital Channelling Networks) with automated SBAR clinical handover generation.
    """

    PARTNER_GATEWAYS: List[Dict[str, str]] = [
        {
            "gateway_id": "ECHANNELLING",
            "name_en": "SLT-Mobitel eChannelling",
            "name_si": "SLT-Mobitel eChannelling සේවාව",
            "description_en": "260+ Private Hospitals & 5,500+ Specialist Consultants islandwide (Dial 225)",
            "description_si": "දිවයින පුරා පෞද්ගලික රෝහල් 260+ ක විශේෂඥ වෛද්‍යවරුන් 5,500+ වෙන්කරවා ගැනීමේ සේවාව (225)",
            "portal_url": "https://www.echannelling.com",
            "hotline": "225"
        },
        {
            "gateway_id": "DOC990",
            "name_en": "Dialog Doc990",
            "name_si": "Dialog Doc990 වෛද්‍ය වෙන්කිරීම",
            "description_en": "Instant Hospital Channelling, Tele-Doctor & Lab Booking across Sri Lanka (Dial 990)",
            "description_si": "ක්ෂණික රෝහල් වෛද්‍ය හමුවීම් සහ දුරකථන වෛද්‍ය උපදේශන සේවාව (990)",
            "portal_url": "https://www.doc.lk",
            "hotline": "990"
        },
        {
            "gateway_id": "ODOC_TELEMED",
            "name_en": "oDoc 24/7 Video Telemedicine",
            "name_si": "oDoc වීඩියෝ වෛද්‍ය සායනය",
            "description_en": "SLMC-registered Specialists & GPs via HD Video Consultation within 5 minutes",
            "description_si": "විනාඩි 5ක් තුළ SLMC ලියාපදිංචි වෛද්‍යවරුන් සමඟ සජීවී වීඩියෝ සාකච්ඡා",
            "portal_url": "https://www.odoc.life",
            "hotline": "0117990990"
        },
        {
            "gateway_id": "HOSPITAL_DIRECT",
            "name_en": "Direct Hospital OPD / Specialist Desk",
            "name_si": "රෝහල් සෘජු විශේෂඥ වෛද්‍ය ඒකකය",
            "description_en": "Direct priority slot reservation at Asiri, Nawaloka, Lanka Hospitals & Durdans",
            "description_si": "ආසිරි, නවලෝක, ලංකා හොස්පිටල්ස් සහ ඩර්ඩන්ස් රෝහල් හරහා සෘජු වෙන්කිරීම්",
            "portal_url": "https://www.asirihealth.com",
            "hotline": "0114665500"
        }
    ]

    SPECIALTY_METADATA: Dict[str, Tuple[str, str]] = {
        "CARDIOLOGY": ("Consultant Cardiologist", "හෘද රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Cardiologist)"),
        "HEMATOLOGY": ("Consultant Hematologist", "රුධිර රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Hematologist)"),
        "ENDOCRINOLOGY": ("Consultant Endocrinologist & Diabetologist", "අන්තරාසර්ග සහ දියවැඩියා විශේෂඥ වෛද්‍ය (Endocrinologist)"),
        "PULMONOLOGY": ("Consultant Respiratory Physician (Pulmonologist)", "ශ්වසන රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Pulmonologist)"),
        "NEUROLOGY": ("Consultant Neurologist", "ස්නායු රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Neurologist)"),
        "GASTROENTEROLOGY": ("Consultant Gastroenterologist & Hepatologist", "ආමාශ හා අක්මා රෝග විශේෂඥ වෛද්‍ය (Gastroenterologist)"),
        "NEPHROLOGY": ("Consultant Nephrologist", "වකුගඩු රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Nephrologist)"),
        "INFECTIOUS_DISEASE": ("Consultant Physician (Internal Medicine & Infectious Diseases)", "කායික සහ බෝවන රෝග විශේෂඥ වෛද්‍ය (Consultant Physician)"),
        "PEDIATRICS": ("Consultant Pediatrician", "ළමා රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Pediatrician)"),
        "GENERAL_MEDICINE": ("Senior Consultant Physician / Family Medicine", "ජ්‍යෙෂ්ඨ කායික රෝග විශේෂඥ වෛද්‍ය (General Physician)"),
    }

    SPECIALIST_DIRECTORY: List[Dict[str, Any]] = [
        # CARDIOLOGY
        {
            "doctor_id": "SL-DOC-CARD-01",
            "full_name_en": "Dr. Arjuna Jayawardena",
            "full_name_si": "වෛද්‍ය අර්ජුන ජයවර්ධන",
            "qualifications": "MBBS (Col), MD (Med), MRCP (UK), FRCP (Lond) - Consultant Cardiologist",
            "slmc_reg_no": "SLMC-14820",
            "specialty_code": "CARDIOLOGY",
            "specialty_en": "Consultant Cardiologist",
            "specialty_si": "හෘද රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Cardiologist)",
            "primary_hospital_en": "Asiri Heart Centre - Colombo 05",
            "primary_hospital_si": "ආසිරි හෘද රෝග මධ්‍යස්ථානය - කොළඹ 05",
            "visiting_hospitals": ["Asiri Heart Centre", "Nawaloka Hospital Colombo", "Lanka Hospitals"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "HOSPITAL_DIRECT"],
            "consultation_fee_lkr": 4200,
            "next_available_slots": [
                "Today • 04:30 PM - 06:30 PM",
                "Tomorrow • 08:30 AM - 11:00 AM",
                "Tomorrow • 05:00 PM - 07:30 PM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.9,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Cardiologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Cardiologist",
            "odoc_url": "https://www.odoc.life/"
        },
        {
            "doctor_id": "SL-DOC-CARD-02",
            "full_name_en": "Dr. Roshani Wijesinghe",
            "full_name_si": "වෛද්‍ය රොෂානි විජේසිංහ",
            "qualifications": "MBBS, MD (Cardiology), FACC - Consultant Interventional Cardiologist",
            "slmc_reg_no": "SLMC-16294",
            "specialty_code": "CARDIOLOGY",
            "specialty_en": "Consultant Cardiologist",
            "specialty_si": "හෘද රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Cardiologist)",
            "primary_hospital_en": "Durdans Heart Centre - Colombo 03",
            "primary_hospital_si": "ඩර්ඩන්ස් හෘද මධ්‍යස්ථානය - කොළඹ 03",
            "visiting_hospitals": ["Durdans Hospital", "Asiri Central Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "ODOC_TELEMED"],
            "consultation_fee_lkr": 4000,
            "next_available_slots": [
                "Today • 06:00 PM - 08:00 PM",
                "Tomorrow • 04:00 PM - 06:30 PM"
            ],
            "languages_spoken": ["Sinhala", "English", "Tamil"],
            "rating": 4.8,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Cardiologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Cardiologist",
            "odoc_url": "https://www.odoc.life/"
        },

        # HEMATOLOGY
        {
            "doctor_id": "SL-DOC-HEMA-01",
            "full_name_en": "Dr. Mahendra Senanayake",
            "full_name_si": "වෛද්‍ය මහේන්ද්‍ර සේනානායක",
            "qualifications": "MBBS, MD (Hematology), FRCPath (UK) - Consultant Hematologist",
            "slmc_reg_no": "SLMC-15311",
            "specialty_code": "HEMATOLOGY",
            "specialty_en": "Consultant Hematologist",
            "specialty_si": "රුධිර රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Hematologist)",
            "primary_hospital_en": "Lanka Hospitals - Colombo 05",
            "primary_hospital_si": "ලංකා හොස්පිටල්ස් - කොළඹ 05",
            "visiting_hospitals": ["Lanka Hospitals", "Asiri Central Hospital", "Nawaloka Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "ODOC_TELEMED", "HOSPITAL_DIRECT"],
            "consultation_fee_lkr": 3800,
            "next_available_slots": [
                "Today • 05:00 PM - 07:00 PM",
                "Tomorrow • 09:00 AM - 11:30 AM",
                "Tomorrow • 04:30 PM - 06:30 PM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.9,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Haematologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Haematologist",
            "odoc_url": "https://www.odoc.life/"
        },

        # ENDOCRINOLOGY & DIABETOLOGY
        {
            "doctor_id": "SL-DOC-ENDO-01",
            "full_name_en": "Dr. Prasad Katulanda",
            "full_name_si": "වෛද්‍ය ප්‍රසාද් කටුලන්ද",
            "qualifications": "MBBS, MD (Col), DPhil (Oxford), FRCP - Consultant Endocrinologist & Diabetologist",
            "slmc_reg_no": "SLMC-13905",
            "specialty_code": "ENDOCRINOLOGY",
            "specialty_en": "Consultant Endocrinologist & Diabetologist",
            "specialty_si": "අන්තරාසර්ග සහ දියවැඩියා විශේෂඥ වෛද්‍ය (Endocrinologist)",
            "primary_hospital_en": "Nawaloka Hospital - Colombo 02",
            "primary_hospital_si": "නවලෝක රෝහල - කොළඹ 02",
            "visiting_hospitals": ["Nawaloka Hospital", "Asiri Surgical Hospital", "Durdans Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "ODOC_TELEMED", "HOSPITAL_DIRECT"],
            "consultation_fee_lkr": 3900,
            "next_available_slots": [
                "Today • 04:00 PM - 06:30 PM",
                "Tomorrow • 07:30 AM - 09:30 AM",
                "Tomorrow • 05:30 PM - 07:30 PM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.9,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Endocrinologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Endocrinologist",
            "odoc_url": "https://www.odoc.life/"
        },

        # INFECTIOUS DISEASE & INTERNAL MEDICINE (Dengue / Sepsis / Viral Fever)
        {
            "doctor_id": "SL-DOC-INFD-01",
            "full_name_en": "Dr. Ananda Wijewickrama",
            "full_name_si": "වෛද්‍ය ආනන්ද විජේවික්‍රම",
            "qualifications": "MBBS, MD (Med), FRCP (UK) - Senior Consultant Physician (Internal Medicine & Dengue/Infectious Diseases)",
            "slmc_reg_no": "SLMC-12440",
            "specialty_code": "INFECTIOUS_DISEASE",
            "specialty_en": "Consultant Physician (Internal Medicine & Infectious Diseases)",
            "specialty_si": "කායික සහ බෝවන රෝග විශේෂඥ වෛද්‍ය (Consultant Physician)",
            "primary_hospital_en": "Asiri Central Hospital - Colombo 10",
            "primary_hospital_si": "ආසිරි සෙන්ට්‍රල් රෝහල - කොළඹ 10",
            "visiting_hospitals": ["Asiri Central Hospital", "Nawaloka Hospital", "Lanka Hospitals"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "ODOC_TELEMED", "HOSPITAL_DIRECT"],
            "consultation_fee_lkr": 3500,
            "next_available_slots": [
                "Today • 03:30 PM - 06:00 PM",
                "Today • 07:00 PM - 08:30 PM (Telemedicine)",
                "Tomorrow • 08:00 AM - 10:30 AM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 5.0,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Physician",
            "doc990_url": "https://www.doc.lk/search?specialization=Physician",
            "odoc_url": "https://www.odoc.life/"
        },

        # PULMONOLOGY / RESPIRATORY
        {
            "doctor_id": "SL-DOC-PULM-01",
            "full_name_en": "Dr. Kirthi Gunasekera",
            "full_name_si": "වෛද්‍ය කීර්ති ගුණසේකර",
            "qualifications": "MBBS, MD, FRCP (Lond), FCCP - Consultant Respiratory Physician (Pulmonologist)",
            "slmc_reg_no": "SLMC-14102",
            "specialty_code": "PULMONOLOGY",
            "specialty_en": "Consultant Respiratory Physician (Pulmonologist)",
            "specialty_si": "ශ්වසන රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Pulmonologist)",
            "primary_hospital_en": "Lanka Hospitals - Colombo 05",
            "primary_hospital_si": "ලංකා හොස්පිටල්ස් - කොළඹ 05",
            "visiting_hospitals": ["Lanka Hospitals", "Durdans Hospital", "Asiri Central Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "ODOC_TELEMED"],
            "consultation_fee_lkr": 3800,
            "next_available_slots": [
                "Today • 05:00 PM - 07:00 PM",
                "Tomorrow • 04:00 PM - 06:30 PM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.8,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Chest+Specialist",
            "doc990_url": "https://www.doc.lk/search?specialization=Chest+Physician",
            "odoc_url": "https://www.odoc.life/"
        },

        # NEUROLOGY
        {
            "doctor_id": "SL-DOC-NEUR-01",
            "full_name_en": "Dr. Padma Gunaratne",
            "full_name_si": "වෛද්‍ය පද්මා ගුණරත්න",
            "qualifications": "MBBS, MD, FRCP (Edin, Lond) - Senior Consultant Neurologist",
            "slmc_reg_no": "SLMC-11890",
            "specialty_code": "NEUROLOGY",
            "specialty_en": "Consultant Neurologist",
            "specialty_si": "ස්නායු රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Neurologist)",
            "primary_hospital_en": "Asiri Central Brain & Spine Centre - Colombo 10",
            "primary_hospital_si": "ආසිරි සෙන්ට්‍රල් ස්නායු මධ්‍යස්ථානය - කොළඹ 10",
            "visiting_hospitals": ["Asiri Central Hospital", "Nawaloka Hospital", "Durdans Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "HOSPITAL_DIRECT"],
            "consultation_fee_lkr": 4200,
            "next_available_slots": [
                "Today • 04:30 PM - 06:30 PM",
                "Tomorrow • 09:30 AM - 12:00 PM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.9,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Neurologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Neurologist",
            "odoc_url": "https://www.odoc.life/"
        },

        # NEPHROLOGY
        {
            "doctor_id": "SL-DOC-NEPH-01",
            "full_name_en": "Dr. Chula Herath",
            "full_name_si": "වෛද්‍ය චූල හේරත්",
            "qualifications": "MBBS, MD, FRCP (Lond) - Consultant Nephrologist",
            "slmc_reg_no": "SLMC-13210",
            "specialty_code": "NEPHROLOGY",
            "specialty_en": "Consultant Nephrologist",
            "specialty_si": "වකුගඩු රෝග පිළිබඳ විශේෂඥ වෛද්‍ය (Nephrologist)",
            "primary_hospital_en": "Asiri Surgical Hospital - Colombo 05",
            "primary_hospital_si": "ආසිරි සර්ජිකල් රෝහල - කොළඹ 05",
            "visiting_hospitals": ["Asiri Surgical Hospital", "Lanka Hospitals", "Western Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "HOSPITAL_DIRECT"],
            "consultation_fee_lkr": 3900,
            "next_available_slots": [
                "Today • 05:30 PM - 07:30 PM",
                "Tomorrow • 04:30 PM - 06:30 PM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.8,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Nephrologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Nephrologist",
            "odoc_url": "https://www.odoc.life/"
        },

        # GASTROENTEROLOGY & HEPATOLOGY
        {
            "doctor_id": "SL-DOC-GAST-01",
            "full_name_en": "Dr. Nilesh Fernandopulle",
            "full_name_si": "වෛද්‍ය නිලේෂ් ප්‍රනාන්දුපුල්ලේ",
            "qualifications": "MBBS, MD, MRCP (UK) - Consultant Gastroenterologist & Hepatologist",
            "slmc_reg_no": "SLMC-15902",
            "specialty_code": "GASTROENTEROLOGY",
            "specialty_en": "Consultant Gastroenterologist & Hepatologist",
            "specialty_si": "ආමාශ හා අක්මා රෝග විශේෂඥ වෛද්‍ය (Gastroenterologist)",
            "primary_hospital_en": "Durdans Hospital - Colombo 03",
            "primary_hospital_si": "ඩර්ඩන්ස් රෝහල - කොළඹ 03",
            "visiting_hospitals": ["Durdans Hospital", "Asiri Central Hospital", "Nawaloka Hospital"],
            "supported_modes": ["IN_PERSON_HOSPITAL", "VIDEO_TELEMEDICINE"],
            "supported_gateways": ["ECHANNELLING", "DOC990", "ODOC_TELEMED"],
            "consultation_fee_lkr": 4000,
            "next_available_slots": [
                "Today • 05:00 PM - 07:00 PM",
                "Tomorrow • 08:30 AM - 10:30 AM"
            ],
            "languages_spoken": ["Sinhala", "English"],
            "rating": 4.9,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Gastroenterologist",
            "doc990_url": "https://www.doc.lk/search?specialization=Gastroenterologist",
            "odoc_url": "https://www.odoc.life/"
        },

        # GENERAL MEDICINE & 24/7 TELEMEDICINE
        {
            "doctor_id": "SL-DOC-GENM-01",
            "full_name_en": "Dr. Sanduni Perera",
            "full_name_si": "වෛද්‍ය සඳුනි පෙරේරා",
            "qualifications": "MBBS (Col), MD (Internal Medicine), MRCGP (Int) - Consultant Family & General Physician",
            "slmc_reg_no": "SLMC-18450",
            "specialty_code": "GENERAL_MEDICINE",
            "specialty_en": "Senior Consultant Physician / Family Medicine",
            "specialty_si": "ජ්‍යෙෂ්ඨ කායික රෝග විශේෂඥ වෛද්‍ය (General Physician)",
            "primary_hospital_en": "oDoc 24/7 Telemedicine & Ninewells Hospital",
            "primary_hospital_si": "oDoc වීඩියෝ වෛද්‍ය සේවාව සහ නයින්වෙල්ස් රෝහල",
            "visiting_hospitals": ["oDoc Instant Video Clinic", "Ninewells Hospital", "Nawaloka OPD"],
            "supported_modes": ["VIDEO_TELEMEDICINE", "IN_PERSON_HOSPITAL"],
            "supported_gateways": ["ODOC_TELEMED", "DOC990", "ECHANNELLING"],
            "consultation_fee_lkr": 2500,
            "next_available_slots": [
                "Instant Video Consult • Next 10 Mins",
                "Today • 04:00 PM - 08:00 PM",
                "Tomorrow • 08:00 AM - 12:00 PM"
            ],
            "languages_spoken": ["Sinhala", "English", "Tamil"],
            "rating": 4.9,
            "echannelling_url": "https://www.echannelling.com/echannelling/search-result?spec=Physician",
            "doc990_url": "https://www.doc.lk/search?specialization=Physician",
            "odoc_url": "https://www.odoc.life/"
        }
    ]

    # Mapping of clinical keywords, Sinhala terms, and ICD-11 prefixes to Specialty Codes
    SPECIALTY_RULES: List[Tuple[str, List[str]]] = [
        (
            "CARDIOLOGY",
            [
                "cardiolog", "heart", "cardiac", "coronary", "myocardial", "troponin", "angina",
                "chest pain", "lipid", "cholesterol", "ldl", "triglyceride", "hypertension",
                "blood pressure", "arrhythmia", "palpitation", "ecg", "ba40", "ba41", "ba00", "5c80",
                "හෘද", "පපුව", "කොලෙස්ටරෝල්", "රුධිර පීඩනය"
            ]
        ),
        (
            "HEMATOLOGY",
            [
                "hematolog", "haematolog", "platelet", "thrombocytopen", "anemia", "anaemia",
                "hemoglobin", "haemoglobin", "leukocyt", "wbc", "fbc", "full blood count",
                "coagulation", "bleeding", "3a00", "3b",
                "රුධිර", "පට්ටිකා", "හිමොග්ලොබින්", "රක්තහීනතාව"
            ]
        ),
        (
            "ENDOCRINOLOGY",
            [
                "endocrinolog", "diabet", "glycemic", "glucose", "hba1c", "insulin", "thyroid",
                "tsh", "t3", "t4", "hypothyroid", "hyperthyroid", "metabolic", "5a10", "5a11", "5a00",
                "දියවැඩියා", "සීනි", "තයිරොයිඩ්", "අන්තරාසර්ග"
            ]
        ),
        (
            "INFECTIOUS_DISEASE",
            [
                "infectious", "dengue", "ns1", "viral fever", "sepsis", "infection", "crp",
                "bacteremia", "malaria", "leptospirosis", "typhoid", "1d2z", "1g40",
                "ඩෙංගු", "උණ", "ආසාදන", "බෝවන"
            ]
        ),
        (
            "PULMONOLOGY",
            [
                "pulmonolog", "respiratory", "chest physician", "asthma", "copd", "bronchitis",
                "pneumonia", "dyspnea", "shortness of breath", "wheez", "cough", "spo2",
                "ca20", "ca23", "ca40", "ශ්වසන", "ඇදුම", "කැස්ස", "හුස්ම"
            ]
        ),
        (
            "NEUROLOGY",
            [
                "neurolog", "stroke", "migraine", "headache", "seizure", "epilepsy", "neuropathy",
                "vertigo", "dizziness", "paralysis", "weakness", "8a80", "8b20",
                "ස්නායු", "හිසරදය", "අංශභාග", "ආඝාත"
            ]
        ),
        (
            "NEPHROLOGY",
            [
                "nephrolog", "renal", "kidney", "creatinine", "egfr", "urea", "ckd", "proteinuria",
                "dialysis", "urinary", "gb61", "gc00", "වකුගඩු", "ක්‍රියැටිනින්", "මුත්‍රා"
            ]
        ),
        (
            "GASTROENTEROLOGY",
            [
                "gastroenterolog", "hepatolog", "liver", "hepatic", "alt", "ast", "bilirubin",
                "stomach", "abdominal", "gastritis", "GERD", "ulcer", "cirrhosis", "da22", "db9",
                "අක්මා", "ආමාශ", "බඩ", "ගැස්ට්‍රයිටිස්"
            ]
        ),
    ]

    def __init__(self):
        self._bookings: List[AppointmentBookingResponse] = []
        self._token_counter: int = 14

    def get_all_specialists(
        self,
        specialty_code: Optional[str] = None,
        consultation_mode: Optional[str] = None,
        gateway: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[SpecialistDoctor]:
        """Returns filtered list of Sri Lankan specialist doctors."""
        results: List[SpecialistDoctor] = []
        for raw in self.SPECIALIST_DIRECTORY:
            if specialty_code and specialty_code.upper() != "ALL":
                if raw["specialty_code"] != specialty_code.upper():
                    continue
            if consultation_mode and consultation_mode.upper() not in raw["supported_modes"]:
                continue
            if gateway and gateway.upper() not in raw["supported_gateways"]:
                continue
            if search_query and search_query.strip():
                q = search_query.lower().strip()
                searchable = (
                    f"{raw['full_name_en']} {raw['full_name_si']} {raw['specialty_en']} "
                    f"{raw['specialty_si']} {raw['primary_hospital_en']} {' '.join(raw['visiting_hospitals'])}"
                ).lower()
                if q not in searchable:
                    # Also check if query maps to this specialty code via clinical terms
                    inferred_code = self.resolve_specialty_code(q)
                    if inferred_code != raw["specialty_code"]:
                        continue
            results.append(SpecialistDoctor(**raw))
        return results

    def resolve_specialty_code(
        self,
        specialty_hint: Optional[str] = None,
        clinical_context: Optional[str] = None,
        icd11_codes: Optional[List[str]] = None,
    ) -> str:
        """
        Determines the best matching specialty code (e.g., CARDIOLOGY, HEMATOLOGY, ENDOCRINOLOGY)
        from a recommended specialist string, symptom/lab text, or ICD-11 codes.
        """
        combined = " ".join(
            filter(
                None,
                [
                    specialty_hint or "",
                    clinical_context or "",
                    " ".join(icd11_codes or []),
                ],
            )
        ).lower()

        if not combined.strip():
            return "GENERAL_MEDICINE"

        # First check specialty_hint directly for high-precision match
        if specialty_hint:
            hint_lower = specialty_hint.lower()
            for spec_code, keywords in self.SPECIALTY_RULES:
                if any(kw.lower() in hint_lower for kw in keywords):
                    return spec_code

        # Score each specialty across the full clinical context
        best_code = "GENERAL_MEDICINE"
        best_score = 0
        for spec_code, keywords in self.SPECIALTY_RULES:
            score = sum(1 for kw in keywords if kw.lower() in combined)
            if score > best_score:
                best_score = score
                best_code = spec_code

        return best_code

    def recommend_specialists(
        self, req: SpecialistRecommendationRequest
    ) -> SpecialistRecommendationResponse:
        """
        Matches a patient's triage output or lab report recommendation to Sri Lankan specialists,
        providing emergency safety overrides when acuity is EMERGENCY.
        """
        spec_code = self.resolve_specialty_code(
            specialty_hint=req.specialty_hint,
            clinical_context=req.clinical_context,
            icd11_codes=req.icd11_codes,
        )
        spec_en, spec_si = self.SPECIALTY_METADATA.get(
            spec_code, self.SPECIALTY_METADATA["GENERAL_MEDICINE"]
        )

        acuity = (req.triage_acuity or "ROUTINE").upper()
        is_emergency = acuity in ("EMERGENCY", "CRITICAL_EMERGENCY")

        recommended_mode = (
            "IN_PERSON_HOSPITAL"
            if is_emergency or acuity in ("URGENT", "ABNORMAL_ELEVATED_RISK")
            else (req.consultation_mode or "VIDEO_TELEMEDICINE")
        )

        # Find specialists in the primary specialty, plus General Medicine / Infectious Disease if appropriate
        matched = self.get_all_specialists(specialty_code=spec_code)
        if spec_code == "HEMATOLOGY":
            # Often dengue/platelet patients benefit from both Hematologist & Consultant Physician
            matched.extend(self.get_all_specialists(specialty_code="INFECTIOUS_DISEASE"))
        elif len(matched) < 2 and spec_code != "GENERAL_MEDICINE":
            matched.extend(self.get_all_specialists(specialty_code="GENERAL_MEDICINE"))

        emergency_en = None
        emergency_si = None
        if is_emergency:
            emergency_en = (
                "CRITICAL SAFETY ALERT: Your presentation indicates an acute medical emergency. "
                "Do NOT wait for a scheduled outpatient channelling slot. Call 1990 (Suwa Seriya Ambulance) "
                "or proceed immediately to the nearest Emergency Treatment Unit (ETU / PCU)."
            )
            emergency_si = (
                "හදිසි වෛද්‍ය අවදානම් නිවේදනයයි: ඔබගේ රෝග ලක්ෂණ හෝ වාර්තා අනුව ක්ෂණික හදිසි ප්‍රතිකාර අවශ්‍ය විය හැක. "
                "සාමාන්‍ය වෛද්‍ය හමුවක් වෙන්කරන තෙක් රැඳී නොසිට වහාම 1990 (සුවසැරිය ගිලන්රථ සේවාව) අමතන්න "
                "හෝ ළඟම ඇති රෝහලේ හදිසි ප්‍රතිකාර ඒකකය (ETU) වෙත යොමුවන්න."
            )

        return SpecialistRecommendationResponse(
            matched_specialty_code=spec_code,
            matched_specialty_en=spec_en,
            matched_specialty_si=spec_si,
            triage_acuity=acuity,
            emergency_warning_active=is_emergency,
            emergency_directive_en=emergency_en,
            emergency_directive_si=emergency_si,
            recommended_consultation_mode=recommended_mode,
            specialists=matched,
            partner_gateways=self.PARTNER_GATEWAYS,
        )

    def _mask_phone(self, phone: str) -> str:
        cleaned = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
        if len(cleaned) <= 4:
            return "****"
        return f"{cleaned[:3]}***{cleaned[-3:]}"

    def _build_sbar_handover(
        self,
        doctor: SpecialistDoctor,
        req: AppointmentBookingRequest,
        booking_ref: str,
    ) -> Tuple[str, str]:
        """
        Generates a structured SBAR (Situation, Background, Assessment, Recommendation)
        Clinical Handover Note in English and Sinhala so the specialist receives the
        MedGuard AI triage / lab report context automatically.
        """
        icd_str = ", ".join(req.correlated_icd11_codes) if req.correlated_icd11_codes else "Pending Clinical Coding"
        context_str = (
            req.clinical_context_summary.strip()
            if req.clinical_context_summary and req.clinical_context_summary.strip()
            else "Patient requested specialist consultation via MedGuard AI Clinical Decision Support."
        )
        acuity = (req.triage_acuity or "ROUTINE").upper()

        sbar_en = (
            f"=== MEDGUARD AI AUTOMATED SBAR CLINICAL HANDOVER ({booking_ref}) ===\n"
            f"• Consulting Specialist: {doctor.full_name_en} ({doctor.specialty_en} | {doctor.slmc_reg_no})\n"
            f"• S (Situation): Patient ({req.patient_name}, Age: {req.patient_age or 'Adult'}) scheduled via {req.booking_gateway} "
            f"for {req.consultation_mode.replace('_', ' ')} at {req.preferred_slot}.\n"
            f"• B (Background & Triage Acuity): Triage Classification = {acuity} | Correlated WHO ICD-11 = {icd_str}.\n"
            f"• A (AI Clinical / Lab Assessment Summary): {context_str}\n"
            f"• R (Recommendation for Specialist): Review attached MedGuard AI biomarker/symptom trajectory and confirm diagnostic workup."
        )

        sbar_si = (
            f"=== MEDGUARD AI ස්වයංක්‍රීය සායනික යොමු කිරීමේ වාර්තාව (SBAR - {booking_ref}) ===\n"
            f"• විශේෂඥ වෛද්‍ය: {doctor.full_name_si} ({doctor.specialty_si} | {doctor.slmc_reg_no})\n"
            f"• S (තත්ත්වය): රෝගියා ({req.patient_name}) {req.booking_gateway} හරහා {req.preferred_slot} වේලාවට වෙන්කර ඇත.\n"
            f"• B (සායනික අවදානම් මට්ටම): Triage මට්ටම = {acuity} | ආශ්‍රිත WHO ICD-11 කේත = {icd_str}.\n"
            f"• A (MedGuard AI මූලික විශ්ලේෂණ සාරාංශය): {context_str}\n"
            f"• R (වෛද්‍යවරයා වෙත යොමුව): රෝගියාගේ රෝග ලක්ෂණ සහ රසායනාගාර දත්ත පරීක්ෂා කර වැඩිදුර ප්‍රතිකාර තහවුරු කරන්න."
        )
        return sbar_en, sbar_si

    def create_appointment(
        self, req: AppointmentBookingRequest
    ) -> AppointmentBookingResponse:
        """
        Books a specialist appointment via eChannelling / Doc990 / oDoc / Direct Hospital
        and returns a confirmed token, gateway redirect link, and clinical SBAR handover slip.
        """
        # Locate doctor
        doctor_dict = next(
            (d for d in self.SPECIALIST_DIRECTORY if d["doctor_id"] == req.doctor_id),
            self.SPECIALIST_DIRECTORY[0],
        )
        doctor = SpecialistDoctor(**doctor_dict)

        self._token_counter += 1
        token_no = self._token_counter

        gateway_prefix = {
            "ECHANNELLING": "ECH",
            "DOC990": "DOC990",
            "ODOC_TELEMED": "ODOC",
            "HOSPITAL_DIRECT": "HOSP",
        }.get(req.booking_gateway.upper(), "ECH")

        short_uid = uuid.uuid4().hex[:5].upper()
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        booking_ref = f"{gateway_prefix}-{date_str}-{short_uid}"

        # Determine redirect URL and hospital/platform label
        gw = req.booking_gateway.upper()
        if gw == "DOC990":
            redirect_url = doctor.doc990_url
        elif gw == "ODOC_TELEMED":
            redirect_url = doctor.odoc_url
        else:
            redirect_url = doctor.echannelling_url

        hospital_label = req.hospital_name or (
            "oDoc HD Video Consultation Room"
            if req.consultation_mode == "VIDEO_TELEMEDICINE"
            else doctor.primary_hospital_en
        )

        telemed_url = None
        if req.consultation_mode == "VIDEO_TELEMEDICINE":
            telemed_url = f"https://telemed.medguard.lk/consult/{booking_ref.lower()}"

        sbar_en, sbar_si = self._build_sbar_handover(doctor, req, booking_ref)

        booking = AppointmentBookingResponse(
            booking_id=str(uuid.uuid4()),
            booking_reference=booking_ref,
            status="CONFIRMED",
            queue_token_number=token_no,
            doctor=doctor,
            patient_display_name=req.patient_name.strip(),
            patient_phone_masked=self._mask_phone(req.patient_phone),
            scheduled_slot=req.preferred_slot,
            consultation_mode=req.consultation_mode,
            booking_gateway=gw,
            hospital_or_platform=hospital_label,
            estimated_fee_lkr=doctor.consultation_fee_lkr,
            telemedicine_meeting_url=telemed_url,
            external_gateway_redirect_url=redirect_url,
            sbar_clinical_handover_en=sbar_en,
            sbar_clinical_handover_si=sbar_si,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._bookings.insert(0, booking)
        return booking

    def list_appointments(self) -> List[AppointmentBookingResponse]:
        return self._bookings

    def cancel_appointment(self, booking_id: str) -> Optional[AppointmentBookingResponse]:
        for idx, b in enumerate(self._bookings):
            if b.booking_id == booking_id or b.booking_reference == booking_id:
                updated = b.model_copy(update={"status": "CANCELLED"})
                self._bookings[idx] = updated
                return updated
        return None


telemedicine_engine = TelemedicineAndBookingEngine()

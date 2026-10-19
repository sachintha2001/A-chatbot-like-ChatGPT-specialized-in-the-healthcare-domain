import pytest
from datetime import datetime, timedelta, timezone
from app.engine.patient_history_engine import PatientHistoryEngine
from app.models.patient import (
    PatientProfile,
    PatientMedicalRecord,
    RelationshipType,
    BiologicalSex,
    MedicalRecordType,
)


class MockRecord:
    def __init__(self, id: str, title: str, record_date: datetime, biomarkers: list):
        self.id = id
        self.title = title
        self.record_date = record_date
        self.extracted_biomarkers = biomarkers


def test_platelet_dengue_recovery_trajectory():
    engine = PatientHistoryEngine()
    now = datetime.now(timezone.utc)

    # 3 sequential records showing platelet nadir and subsequent recovery
    records = [
        MockRecord(
            id="rec-1",
            title="Day 3 Critical Nadir",
            record_date=now - timedelta(days=2),
            biomarkers=[{
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "numeric_value": 42000.0,
                "unit": "/uL",
                "status": "CRITICAL_LOW",
                "is_abnormal": True,
                "is_critical": True
            }]
        ),
        MockRecord(
            id="rec-2",
            title="Day 4 Early Recovery",
            record_date=now - timedelta(days=1),
            biomarkers=[{
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "numeric_value": 78000.0,
                "unit": "/uL",
                "status": "DECREASED",
                "is_abnormal": True,
                "is_critical": False
            }]
        ),
        MockRecord(
            id="rec-3",
            title="Day 5 Discharge Evaluation",
            record_date=now,
            biomarkers=[{
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "display_name_si": "පට්ටිකා ප්‍රමාණය",
                "numeric_value": 148000.0,
                "unit": "/uL",
                "status": "DECREASED",
                "is_abnormal": True,
                "is_critical": False
            }]
        ),
    ]

    result = engine.compute_longitudinal_trends(records)
    assert result["total_records_analyzed"] == 3
    assert result["tracked_biomarkers_count"] == 1

    trend = result["trends"][0]
    assert trend["canonical_id"] == "platelets"
    assert trend["baseline_value"] == 42000.0
    assert trend["previous_value"] == 78000.0
    assert trend["latest_value"] == 148000.0
    assert trend["delta_value"] == 70000.0
    assert trend["delta_percentage"] == round((70000.0 / 78000.0) * 100, 1)
    assert trend["trajectory"] == "IMPROVING"
    assert "recovering" in trend["trajectory_label_en"].lower() or "recovery" in trend["trajectory_label_en"].lower()
    assert "පට්ටිකා" in trend["trajectory_label_si"]
    assert len(trend["data_points"]) == 3


def test_platelet_deterioration_trajectory():
    engine = PatientHistoryEngine()
    now = datetime.now(timezone.utc)

    records = [
        MockRecord(
            id="rec-1",
            title="Day 1 Baseline",
            record_date=now - timedelta(days=2),
            biomarkers=[{
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "numeric_value": 180000.0,
                "unit": "/uL",
                "status": "NORMAL",
                "is_abnormal": False,
                "is_critical": False
            }]
        ),
        MockRecord(
            id="rec-2",
            title="Day 2 Decline",
            record_date=now - timedelta(days=1),
            biomarkers=[{
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "numeric_value": 90000.0,
                "unit": "/uL",
                "status": "DECREASED",
                "is_abnormal": True,
                "is_critical": False
            }]
        ),
        MockRecord(
            id="rec-3",
            title="Day 3 Critical Drop",
            record_date=now,
            biomarkers=[{
                "canonical_id": "platelets",
                "display_name_en": "Platelet Count",
                "numeric_value": 35000.0,
                "unit": "/uL",
                "status": "CRITICAL_LOW",
                "is_abnormal": True,
                "is_critical": True
            }]
        ),
    ]

    result = engine.compute_longitudinal_trends(records)
    trend = result["trends"][0]
    assert trend["trajectory"] == "CRITICAL_ATTENTION"
    assert trend["delta_value"] == -55000.0
    assert result["overall_trajectory"] == "REQUIRES_ATTENTION"


def test_glycemic_and_lipid_longitudinal_trends():
    engine = PatientHistoryEngine()
    now = datetime.now(timezone.utc)

    records = [
        MockRecord(
            id="rec-1",
            title="Baseline Panel",
            record_date=now - timedelta(days=90),
            biomarkers=[
                {
                    "canonical_id": "fbs",
                    "display_name_en": "Fasting Blood Sugar",
                    "numeric_value": 210.0,
                    "unit": "mg/dL",
                    "status": "CRITICAL_HIGH",
                    "is_abnormal": True,
                    "is_critical": True
                },
                {
                    "canonical_id": "hba1c",
                    "display_name_en": "HbA1c",
                    "numeric_value": 9.4,
                    "unit": "%",
                    "status": "CRITICAL_HIGH",
                    "is_abnormal": True,
                    "is_critical": True
                },
                {
                    "canonical_id": "cholesterol_total",
                    "display_name_en": "Total Cholesterol",
                    "numeric_value": 268.0,
                    "unit": "mg/dL",
                    "status": "ELEVATED",
                    "is_abnormal": True,
                    "is_critical": False
                }
            ]
        ),
        MockRecord(
            id="rec-2",
            title="Follow-up Panel",
            record_date=now,
            biomarkers=[
                {
                    "canonical_id": "fbs",
                    "display_name_en": "Fasting Blood Sugar",
                    "numeric_value": 124.0,
                    "unit": "mg/dL",
                    "status": "ELEVATED",
                    "is_abnormal": True,
                    "is_critical": False
                },
                {
                    "canonical_id": "hba1c",
                    "display_name_en": "HbA1c",
                    "numeric_value": 6.9,
                    "unit": "%",
                    "status": "ELEVATED",
                    "is_abnormal": True,
                    "is_critical": False
                },
                {
                    "canonical_id": "cholesterol_total",
                    "display_name_en": "Total Cholesterol",
                    "numeric_value": 184.0,
                    "unit": "mg/dL",
                    "status": "NORMAL",
                    "is_abnormal": False,
                    "is_critical": False
                }
            ]
        ),
    ]

    result = engine.compute_longitudinal_trends(records)
    assert result["tracked_biomarkers_count"] == 3

    trends_map = {t["canonical_id"]: t for t in result["trends"]}

    # FBS should be improving (down from 210 to 124)
    assert trends_map["fbs"]["trajectory"] == "IMPROVING"
    assert trends_map["fbs"]["delta_value"] == -86.0

    # HbA1c should be improving (down from 9.4 to 6.9)
    assert trends_map["hba1c"]["trajectory"] == "IMPROVING"
    assert trends_map["hba1c"]["delta_value"] == -2.5

    # Cholesterol should be stable / normal
    assert trends_map["cholesterol_total"]["trajectory"] == "STABLE"
    assert trends_map["cholesterol_total"]["delta_value"] == -84.0

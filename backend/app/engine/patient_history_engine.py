from typing import Dict, Any, List, Optional
from datetime import datetime
from app.knowledge.lab_biomarkers import CLINICAL_BIOMARKER_REGISTRY


class PatientHistoryEngine:
    """
    Clinical Longitudinal Health Record & Biomarker Trend Trajectory Analysis Engine.
    Aggregates historical laboratory measurements and clinical triage checkpoints,
    calculates mathematical deltas and percentage changes, determines physiological
    improvement or deterioration trajectories, and generates bilingual clinical summaries.
    """

    def __init__(self):
        self.registry = CLINICAL_BIOMARKER_REGISTRY
        self.lookup_map: Dict[str, Dict[str, Any]] = {}
        for key, data in CLINICAL_BIOMARKER_REGISTRY.items():
            self.lookup_map[key.lower()] = data
            canonical = data.get("canonical_id")
            if canonical:
                self.lookup_map[canonical.lower()] = data
            for alias in data.get("aliases", []):
                self.lookup_map[alias.lower()] = data

    def _get_meta(self, canonical_id: str) -> Dict[str, Any]:
        cleaned = canonical_id.lower().strip()
        if cleaned in self.lookup_map:
            return self.lookup_map[cleaned]
        cleaned_space = cleaned.replace("_", " ")
        if cleaned_space in self.lookup_map:
            return self.lookup_map[cleaned_space]
        cleaned_underscore = cleaned.replace(" ", "_")
        if cleaned_underscore in self.lookup_map:
            return self.lookup_map[cleaned_underscore]
        return {}

    def compute_longitudinal_trends(
        self,
        records: List[Any],
        patient_profile: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Processes a list of PatientMedicalRecord objects and produces comprehensive
        time-series trajectory intelligence across all identified quantitative biomarkers.
        """
        # Collect all biomarker measurements grouped by canonical_id
        # Records are passed in or sorted chronologically (oldest to newest)
        sorted_records = sorted(
            records,
            key=lambda r: r.record_date if isinstance(r.record_date, datetime) else datetime.fromisoformat(str(r.record_date))
        )

        biomarker_series: Dict[str, List[Dict[str, Any]]] = {}

        for record in sorted_records:
            record_id = str(record.id)
            record_title = record.title
            record_date_str = (
                record.record_date.isoformat()
                if isinstance(record.record_date, datetime)
                else str(record.record_date)
            )

            biomarkers = record.extracted_biomarkers or []
            for item in biomarkers:
                canonical_id = item.get("canonical_id")
                if not canonical_id:
                    raw_id = item.get("display_name_en") or ""
                    meta = self._get_meta(raw_id)
                    canonical_id = meta.get("canonical_id") or raw_id.lower().replace(" ", "_")
                numeric_val = item.get("numeric_value")

                if not canonical_id or numeric_val is None:
                    continue

                try:
                    num_float = float(numeric_val)
                except (ValueError, TypeError):
                    continue

                if canonical_id not in biomarker_series:
                    biomarker_series[canonical_id] = []

                biomarker_series[canonical_id].append({
                    "record_id": record_id,
                    "record_title": record_title,
                    "date": record_date_str,
                    "value": num_float,
                    "unit": item.get("unit", ""),
                    "status": item.get("status", "NORMAL"),
                    "status_si": item.get("status_si", "සාමාන්‍ය"),
                    "is_abnormal": bool(item.get("is_abnormal", False)),
                    "is_critical": bool(item.get("is_critical", False)),
                    "display_name_en": item.get("display_name_en") or self._get_display_name_en(canonical_id),
                    "display_name_si": item.get("display_name_si") or self._get_display_name_si(canonical_id),
                    "ref_interval": item.get("ref_interval", "")
                })

        # Calculate trajectories for each biomarker
        tracked_trends: List[Dict[str, Any]] = []

        for canonical_id, points in biomarker_series.items():
            if not points:
                continue

            registry_meta = self._get_meta(canonical_id)
            unit = points[-1]["unit"] or registry_meta.get("unit", "")
            display_name_en = points[-1]["display_name_en"]
            display_name_si = points[-1]["display_name_si"]
            ref_interval = points[-1]["ref_interval"] or f"{registry_meta.get('ref_min', '')} - {registry_meta.get('ref_max', '')}"

            baseline_pt = points[0]
            latest_pt = points[-1]
            previous_pt = points[-2] if len(points) >= 2 else None

            latest_val = latest_pt["value"]
            previous_val = previous_pt["value"] if previous_pt else latest_val
            baseline_val = baseline_pt["value"]

            delta_val = round(latest_val - previous_val, 2)
            delta_pct = (
                round(((latest_val - previous_val) / previous_val) * 100, 1)
                if previous_val != 0
                else 0.0
            )

            trajectory_info = self._calculate_trajectory(
                canonical_id=canonical_id,
                baseline_val=baseline_val,
                previous_val=previous_val,
                latest_val=latest_val,
                latest_pt=latest_pt,
                registry_meta=registry_meta,
                delta_val=delta_val,
                delta_pct=delta_pct,
                num_points=len(points)
            )

            tracked_trends.append({
                "canonical_id": canonical_id,
                "display_name_en": display_name_en,
                "display_name_si": display_name_si,
                "category": registry_meta.get("category", "General"),
                "unit": unit,
                "ref_interval": ref_interval,
                "data_points": points,
                "point_count": len(points),
                "baseline_value": baseline_val,
                "previous_value": previous_val,
                "latest_value": latest_val,
                "delta_value": delta_val,
                "delta_percentage": delta_pct,
                "trajectory": trajectory_info["status"],
                "trajectory_label_en": trajectory_info["label_en"],
                "trajectory_label_si": trajectory_info["label_si"],
                "clinical_insight_en": trajectory_info["insight_en"],
                "clinical_insight_si": trajectory_info["insight_si"],
                "is_abnormal": latest_pt["is_abnormal"],
                "is_critical": latest_pt["is_critical"]
            })

        # Sort trends: critical/abnormal first, then by point count descending
        tracked_trends.sort(
            key=lambda t: (t["is_critical"], t["is_abnormal"], t["point_count"]),
            reverse=True
        )

        # Profile level longitudinal summary
        improving_count = sum(1 for t in tracked_trends if t["trajectory"] == "IMPROVING")
        deteriorating_count = sum(1 for t in tracked_trends if t["trajectory"] in ("DETERIORATING", "CRITICAL_ATTENTION"))
        critical_count = sum(1 for t in tracked_trends if t["is_critical"])

        if critical_count > 0 or deteriorating_count >= 2:
            overall_trajectory = "REQUIRES_ATTENTION"
            overall_trajectory_en = "Active Medical Attention Required (Deteriorating or Panic Values Detected)"
            overall_trajectory_si = "ක්‍රියාකාරී වෛද්‍ය අවධානයක් අවශ්‍යයි (අහිතකර ප්‍රවණතා හෝ අවදානම් අගයන් හඳුනාගෙන ඇත)"
        elif improving_count > 0 and deteriorating_count == 0:
            overall_trajectory = "IMPROVING"
            overall_trajectory_en = "Favorable Clinical Recovery Trajectory Observed"
            overall_trajectory_si = "හිතකර සායනික සුවවීමේ ප්‍රවණතාවයක් පෙන්නුම් කරයි"
        else:
            overall_trajectory = "STABLE"
            overall_trajectory_en = "Clinical Parameters Stable Across Monitored Records"
            overall_trajectory_si = "පරීක්ෂා කරන ලද කාලසීමාව තුළ සායනික අගයන් ස්ථාවර මට්ටමක පවතී"

        return {
            "total_records_analyzed": len(sorted_records),
            "tracked_biomarkers_count": len(tracked_trends),
            "overall_trajectory": overall_trajectory,
            "overall_trajectory_en": overall_trajectory_en,
            "overall_trajectory_si": overall_trajectory_si,
            "improving_count": improving_count,
            "deteriorating_count": deteriorating_count,
            "critical_count": critical_count,
            "trends": tracked_trends
        }

    def _calculate_trajectory(
        self,
        canonical_id: str,
        baseline_val: float,
        previous_val: float,
        latest_val: float,
        latest_pt: Dict[str, Any],
        registry_meta: Dict[str, Any],
        delta_val: float,
        delta_pct: float,
        num_points: int
    ) -> Dict[str, str]:
        """
        Determines the clinical trajectory direction considering the specific physiological
        directionality of the biomarker (e.g. platelets rising is improving; glucose rising is deteriorating).
        """
        if num_points < 2:
            status = "STABLE"
            if latest_pt["is_critical"]:
                status = "CRITICAL_ATTENTION"
                label_en = "Single critical baseline reading"
                label_si = "තනි තීරණාත්මක ආරම්භක අගයක්"
                insight_en = "Initial measurement is in the critical panic interval. Longitudinal tracking initiated."
                insight_si = "පළමු අගය අවදානම් සීමාවේ පවතී. අඛණ්ඩ කාලානුක්‍රමික නිරීක්ෂණය ආරම්භ කරන ලදී."
            elif latest_pt["is_abnormal"]:
                label_en = "Single abnormal baseline reading"
                label_si = "තනි අසාමාන්‍ය ආරම්භක අගයක්"
                insight_en = "Baseline measurement is outside normal physiological reference intervals."
                insight_si = "ආරම්භක අගය සාමාන්‍ය නිරෝගී සීමාවෙන් පරිබාහිරව පවතී."
            else:
                label_en = "Normal baseline recording"
                label_si = "සාමාන්‍ය ආරම්භක සටහනක්"
                insight_en = "Baseline parameter is within normal physiological limits."
                insight_si = "ආරම්භක පරාමිතිය සාමාන්‍ය නිරෝගී සීමාව තුළ පවතී."

            return {
                "status": status,
                "label_en": label_en,
                "label_si": label_si,
                "insight_en": insight_en,
                "insight_si": insight_si
            }

        ref_low = registry_meta.get("ref_min", 0.0)
        ref_high = registry_meta.get("ref_max", 999999.0)

        # 1. Platelets (Thrombocytopenia monitoring in Dengue)
        if canonical_id == "platelets":
            if latest_val < 50000:
                if delta_val > 0:
                    status = "IMPROVING"
                    label_en = f"Platelet count recovering from critical nadir (+{int(delta_val):,} /uL, +{delta_pct}%)"
                    label_si = f"තීරණාත්මක මට්ටමෙන් පසු පට්ටිකා නැවත ඉහළ යමින් පවතී (+{int(delta_val):,} /uL, +{delta_pct}%)"
                    insight_en = "Platelet count demonstrates early bone marrow recovery. Continue strict fluid balance monitoring."
                    insight_si = "පට්ටිකා මට්ටම යථා තත්ත්වයට පත්වීමේ සලකුණු පෙන්වයි. දියර සමතුලිතතාවය සහ විවේකය දිගටම පවත්වා ගන්න."
                else:
                    status = "CRITICAL_ATTENTION"
                    label_en = f"Severe thrombocytopenia declining ({int(delta_val):,} /uL, {delta_pct}%)"
                    label_si = f"පට්ටිකා මට්ටම තවදුරටත් අවදානම් ලෙස පහත වැටේ ({int(delta_val):,} /uL, {delta_pct}%)"
                    insight_en = "Critical thrombocytopenia (<50,000 /uL). High hemorrhage risk in acute dengue fever."
                    insight_si = "පට්ටිකා අගය 50,000ට වඩා අඩුයි. රුධිර වහනය වැළැක්වීමට වහාම රෝහල්ගත අධීක්ෂණය අවශ්‍යයි."
            elif latest_val < 150000:
                if delta_val > 0:
                    status = "IMPROVING"
                    label_en = f"Platelet recovery in progress (+{int(delta_val):,} /uL, +{delta_pct}%)"
                    label_si = f"පට්ටිකා ප්‍රකෘතිමත් වීම ප්‍රගතියක් පෙන්වයි (+{int(delta_val):,} /uL, +{delta_pct}%)"
                    insight_en = "Platelet trajectory is positive and advancing towards standard reference minimum (150,000 /uL)."
                    insight_si = "පට්ටිකා මට්ටම යහපත් දිශාවට වර්ධනය වන අතර සාමාන්‍ය අවම සීමාව (150,000) දෙසට ළඟාවේ."
                else:
                    status = "DETERIORATING"
                    label_en = f"Platelets dropping below normal ({int(delta_val):,} /uL, {delta_pct}%)"
                    label_si = f"පට්ටිකා මට්ටම පහත වැටෙමින් පවතී ({int(delta_val):,} /uL, {delta_pct}%)"
                    insight_en = "Platelets show a downward trend. Daily FBC monitoring is clinically indicated."
                    insight_si = "පට්ටිකා පහළ බසින ප්‍රවණතාවයක් පෙන්වයි. දිනපතා සම්පූර්ණ රුධිර පරීක්ෂාව (FBC) සිදු කළ යුතුය."
            else:
                status = "STABLE"
                label_en = "Platelet count maintained within normal reference interval"
                label_si = "පට්ටිකා මට්ටම සාමාන්‍ය නිරෝගී සීමාව තුළ ස්ථාවරයි"
                insight_en = f"Current count ({int(latest_val):,} /uL) is fully within normal physiological range."
                insight_si = f"වර්තමාන අගය ({int(latest_val):,} /uL) සාමාන්‍ය නිරෝගී පරාසයේ පවතී."

            return {
                "status": status,
                "label_en": label_en,
                "label_si": label_si,
                "insight_en": insight_en,
                "insight_si": insight_si
            }

        # 2. Glycemic Indicators (Fasting Blood Sugar, HbA1c)
        if canonical_id in ("fbs", "fasting_blood_sugar", "hba1c"):
            if latest_val > ref_high:
                if delta_val < 0:
                    status = "IMPROVING"
                    label_en = f"Glycemic level improving towards target ({delta_val} {latest_pt['unit']}, {delta_pct}%)"
                    label_si = f"රුධිර සීනි මට්ටම සාමාන්‍ය ඉලක්කය දෙසට යහපත් වෙමින් පවතී ({delta_val} {latest_pt['unit']}, {delta_pct}%)"
                    insight_en = "Downward trajectory indicates therapeutic response to lifestyle modification or pharmacotherapy."
                    insight_si = "අගය පහත වැටීම මඟින් ඖෂධ හෝ ආහාර පාලනයට ලැබෙන යහපත් ප්‍රතිචාරය සනාථ වේ."
                else:
                    status = "DETERIORATING"
                    label_en = f"Glycemic elevation worsening (+{delta_val} {latest_pt['unit']}, +{delta_pct}%)"
                    label_si = f"රුධිර සීනි මට්ටම තවදුරටත් ඉහළ යමින් පවතී (+{delta_val} {latest_pt['unit']}, +{delta_pct}%)"
                    insight_en = "Suboptimal glycemic control. Clinical review of anti-hyperglycemic regimen is recommended."
                    insight_si = "සීනි පාලනය ප්‍රමාණවත් නොවේ. වෛද්‍යවරයා හමුවී ඖෂධ මාත්‍රාව සමාලෝචනය කිරීම සුදුසුය."
            else:
                status = "STABLE"
                label_en = f"Optimal glycemic control achieved ({latest_val} {latest_pt['unit']})"
                label_si = f"රුධිර සීනි මට්ටම නිරෝගී පරාසය තුළ මනාව පාලනය වී ඇත ({latest_val} {latest_pt['unit']})"
                insight_en = "Current parameter is within ADA clinical target guidelines."
                insight_si = "වර්තමාන අගය පිළිගත් ADA සායනික නිර්දේශිත සීමාව තුළ පවතී."

            return {
                "status": status,
                "label_en": label_en,
                "label_si": label_si,
                "insight_en": insight_en,
                "insight_si": insight_si
            }

        # 3. Lipid Profile (Total Cholesterol, LDL, Triglycerides)
        if canonical_id in ("total_cholesterol", "cholesterol_total", "ldl_cholesterol", "triglycerides"):
            if latest_val > ref_high:
                if delta_val < 0:
                    status = "IMPROVING"
                    label_en = f"Lipid levels decreasing towards cardiovascular target ({delta_val} {latest_pt['unit']}, {delta_pct}%)"
                    label_si = f"මේද මට්ටම හෘද සෞඛ්‍ය ඉලක්කය දෙසට අඩුවෙමින් පවතී ({delta_val} {latest_pt['unit']}, {delta_pct}%)"
                    insight_en = "Favorable lipid reduction trajectory reduces atherogenic risk."
                    insight_si = "කොලෙස්ටරෝල් අඩුවීමේ ප්‍රවණතාව හෘදයාබාධ අවදානම අවම කිරීමට උපකාරී වේ."
                else:
                    status = "DETERIORATING"
                    label_en = f"Lipid levels rising (+{delta_val} {latest_pt['unit']}, +{delta_pct}%)"
                    label_si = f"මේද මට්ටම තවදුරටත් ඉහළ යමින් පවතී (+{delta_val} {latest_pt['unit']}, +{delta_pct}%)"
                    insight_en = "Elevated atherogenic index. Dietary adjustment or statin therapy re-evaluation advised."
                    insight_si = "අහිතකර මේදය වැඩිවීම හෘද නාල අවහිර වීමේ අවදානම වැඩි කරයි. ආහාර පාලනය ශක්තිමත් කරන්න."
            else:
                status = "STABLE"
                label_en = "Lipid parameters maintained within desirable range"
                label_si = "මේද මට්ටම නිරෝගී පරාසය තුළ ස්ථාවරව පවතී"
                insight_en = "Atherogenic cardiovascular risk parameters are well controlled."
                insight_si = "හෘද සෞඛ්‍ය අවදානම් පරාමිතීන් යහපත් මට්ටමක පවත්වාගෙන යයි."

            return {
                "status": status,
                "label_en": label_en,
                "label_si": label_si,
                "insight_en": insight_en,
                "insight_si": insight_si
            }

        # 4. Renal Function (Creatinine)
        if canonical_id in ("serum_creatinine", "blood_urea_nitrogen"):
            if latest_val > ref_high:
                if delta_val < 0:
                    status = "IMPROVING"
                    label_en = f"Renal filtration biomarker improving ({delta_val} {latest_pt['unit']})"
                    label_si = f"වකුගඩු පෙරීමේ හැකියාව යහපත් අතට හැරෙමින් පවතී ({delta_val} {latest_pt['unit']})"
                    insight_en = "Decreasing creatinine indicates stabilizing renal perfusion and clearance."
                    insight_si = "ක්‍රියේටිනින් අඩුවීම මඟින් වකුගඩු ක්‍රියාකාරීත්වය යහපත් වන බව පෙන්නුම් කෙරේ."
                else:
                    status = "DETERIORATING"
                    label_en = f"Renal biomarker elevation (+{delta_val} {latest_pt['unit']})"
                    label_si = f"වකුගඩු ක්‍රියේටිනින් අගය ඉහළ යයි (+{delta_val} {latest_pt['unit']})"
                    insight_en = "Rising serum creatinine may indicate acute kidney injury or worsening chronic nephropathy."
                    insight_si = "ක්‍රියේටිනින් ඉහළ යාම වකුගඩු ක්‍රියාකාරීත්වය දුර්වල වන බවට අනතුරු අඟවයි."
            else:
                status = "STABLE"
                label_en = "Renal function biomarkers within physiological reference limits"
                label_si = "වකුගඩු ක්‍රියාකාරීත්ව අගයන් සාමාන්‍ය නිරෝගී මට්ටමේ පවතී"
                insight_en = "Normal baseline glomerular clearance supported."
                insight_si = "සාමාන්‍ය නිරෝගී වකුගඩු පෙරීමේ හැකියාව තහවුරු කෙරේ."

            return {
                "status": status,
                "label_en": label_en,
                "label_si": label_si,
                "insight_en": insight_en,
                "insight_si": insight_si
            }

        # 5. Hemoglobin (Anemia monitoring)
        if canonical_id == "hemoglobin":
            if latest_val < ref_low:
                if delta_val > 0:
                    status = "IMPROVING"
                    label_en = f"Hemoglobin recovering from anemia (+{delta_val} g/dL, +{delta_pct}%)"
                    label_si = f"රක්තහීනතාවයෙන් පසු හීමොග්ලොබින් මට්ටම ඉහළ යයි (+{delta_val} g/dL, +{delta_pct}%)"
                    insight_en = "Positive red cell mass recovery in response to nutritional or hematinic therapy."
                    insight_si = "පෝෂණ හෝ යකඩ ප්‍රතිකාර සමඟ රතු රුධිර සෛල ප්‍රමාණය සාර්ථකව වර්ධනය වේ."
                else:
                    status = "DETERIORATING"
                    label_en = f"Hemoglobin dropping further ({delta_val} g/dL, {delta_pct}%)"
                    label_si = f"හීමොග්ලොබින් මට්ටම තවදුරටත් පහත වැටෙමින් පවතී ({delta_val} g/dL, {delta_pct}%)"
                    insight_en = "Worsening anemia. Evaluation for occult blood loss or nutritional deficiency advised."
                    insight_si = "රක්තහීනතාවය වැඩිවේ. රුධිර වහනයක් හෝ යකඩ ඌනතාවයක් ඇත්දැයි වෛද්‍ය පරීක්ෂාව අවශ්‍යයි."
            elif latest_val > ref_high:
                status = "DETERIORATING"
                label_en = f"Hemoglobin elevated (hemoconcentration risk: {latest_val} g/dL)"
                label_si = f"හීමොග්ලොබින් අධිකයි (රුධිර සාන්ද්‍රණය වැඩිවීම: {latest_val} g/dL)"
                insight_en = "Elevated hemoglobin may indicate hemoconcentration / plasma leakage in dengue or polycythemia."
                insight_si = "හීමොග්ලොබින් අධික වීම ඩෙංගු රෝගයේදී ප්ලාස්මා කාන්දු වීමක් හෝ විජලනයක් විය හැක."
            else:
                status = "STABLE"
                label_en = "Hemoglobin stable within healthy physiological reference range"
                label_si = "හීමොග්ලොබින් නිරෝගී සාමාන්‍ය පරාසය තුළ ස්ථාවරයි"
                insight_en = f"Oxygen carrying capacity is normal ({latest_val} g/dL)."
                insight_si = f"රුධිරයේ ඔක්සිජන් පරිවහන ධාරිතාව සාමාන්‍ය මට්ටමක පවතී ({latest_val} g/dL)."

            return {
                "status": status,
                "label_en": label_en,
                "label_si": label_si,
                "insight_en": insight_en,
                "insight_si": insight_si
            }

        # Generic default for other biomarkers (e.g. ALT, WBC, Potassium, CRP)
        if abs(delta_val) < 0.01:
            status = "STABLE"
            label_en = "Value remains constant across readings"
            label_si = "පරීක්ෂණ අතරතුර අගය නොවෙනස්ව පවතී"
            insight_en = "Parameter displays physiological stability."
            insight_si = "පරාමිතිය ස්ථාවර මට්ටමක් පෙන්නුම් කරයි."
        elif latest_val > ref_high:
            if delta_val < 0:
                status = "IMPROVING"
                label_en = f"Elevated value decreasing towards normal ({delta_val} {latest_pt['unit']})"
                label_si = f"අධික අගය සාමාන්‍ය මට්ටම දෙසට අඩුවෙමින් පවතී ({delta_val} {latest_pt['unit']})"
                insight_en = "Favorable therapeutic response observed."
                insight_si = "ප්‍රතිකාර සඳහා හිතකර ප්‍රතිචාරයක් පෙන්නුම් කරයි."
            else:
                status = "DETERIORATING"
                label_en = f"Parameter elevation increasing (+{delta_val} {latest_pt['unit']})"
                label_si = f"අගය තවදුරටත් ඉහළ යමින් පවතී (+{delta_val} {latest_pt['unit']})"
                insight_en = "Biomarker remains above clinical safety limits."
                insight_si = "පරීක්ෂණ අගය සායනික ආරක්ෂිත සීමාවට වඩා ඉහළින් පවතී."
        elif latest_val < ref_low:
            if delta_val > 0:
                status = "IMPROVING"
                label_en = f"Low parameter rising towards normal (+{delta_val} {latest_pt['unit']})"
                label_si = f"අඩු අගය සාමාන්‍ය මට්ටම දෙසට ඉහළ යයි (+{delta_val} {latest_pt['unit']})"
                insight_en = "Parameter demonstrating normalization trajectory."
                insight_si = "අගය සාමාන්‍ය මට්ටමට ළඟාවීමේ ප්‍රවණතාවයක් පෙන්වයි."
            else:
                status = "DETERIORATING"
                label_en = f"Parameter dropping further ({delta_val} {latest_pt['unit']})"
                label_si = f"අගය තවදුරටත් පහත වැටෙමින් පවතී ({delta_val} {latest_pt['unit']})"
                insight_en = "Parameter remains suppressed below reference bounds."
                insight_si = "අගය සාමාන්‍ය අවම සීමාවට වඩා අඩුව පවතී."
        else:
            status = "STABLE"
            label_en = f"Parameter maintained within reference bounds ({latest_val} {latest_pt['unit']})"
            label_si = f"පරාමිතිය සාමාන්‍ය සීමාව තුළ ස්ථාවරව පවතී ({latest_val} {latest_pt['unit']})"
            insight_en = "Parameter is physiologically normal."
            insight_si = "පරාමිතිය සාමාන්‍ය නිරෝගී මට්ටමක පවතී."

        return {
            "status": status,
            "label_en": label_en,
            "label_si": label_si,
            "insight_en": insight_en,
            "insight_si": insight_si
        }

    def _get_display_name_en(self, canonical_id: str) -> str:
        reg = self._get_meta(canonical_id)
        return reg.get("display_name_en", canonical_id.replace("_", " ").title()) if reg else canonical_id.replace("_", " ").title()

    def _get_display_name_si(self, canonical_id: str) -> str:
        reg = self._get_meta(canonical_id)
        return reg.get("display_name_si", canonical_id.replace("_", " ")) if reg else canonical_id.replace("_", " ")


patient_history_engine = PatientHistoryEngine()

"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  User,
  Users,
  Plus,
  Activity,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
  CheckCircle2,
  Clock,
  Calendar,
  ShieldAlert,
  FileText,
  Phone,
  RefreshCw,
  X,
  ChevronRight,
  Sparkles,
  Heart,
  Droplet
} from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import {
  PatientProfileItem,
  PatientMedicalRecordItem,
  PatientTrendsResponse,
  BiomarkerTrendItem,
  BiomarkerDataPoint
} from "@/lib/types";
import {
  fetchPatientProfiles,
  fetchPatientProfile,
  fetchPatientRecords,
  fetchPatientTrends,
  createPatientProfile,
  createPatientRecord
} from "@/lib/api";

// Helper for Age calculation from YYYY-MM-DD
function calculateAge(dobString?: string | null): number | null {
  if (!dobString) return null;
  const dob = new Date(dobString);
  if (isNaN(dob.getTime())) return null;
  const diff = Date.now() - dob.getTime();
  const ageDate = new Date(diff);
  return Math.abs(ageDate.getUTCFullYear() - 1970);
}

// Sparkline Component for Biomarker Trajectory
function BiomarkerSparkline({
  points,
  trajectory,
  unit,
  refInterval
}: {
  points: BiomarkerDataPoint[];
  trajectory: string;
  unit: string;
  refInterval: string;
}) {
  const [activePoint, setActivePoint] = useState<BiomarkerDataPoint | null>(null);

  if (!points || points.length === 0) {
    return <div className="h-28 flex items-center justify-center text-xs text-slate-400">No data points</div>;
  }

  const values = points.map((p) => p.value);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const padding = (maxVal - minVal) * 0.15 || (minVal * 0.1) || 1;
  const chartMin = Math.max(0, minVal - padding);
  const chartMax = maxVal + padding;
  const valRange = chartMax - chartMin || 1;

  const width = 340;
  const height = 90;
  const padX = 20;
  const padY = 14;

  const coords = points.map((pt, idx) => {
    const x = points.length === 1 ? width / 2 : padX + (idx / (points.length - 1)) * (width - padX * 2);
    const y = height - padY - ((pt.value - chartMin) / valRange) * (height - padY * 2);
    return { x, y, pt };
  });

  const pathD = coords.reduce((acc, curr, idx) => {
    return idx === 0 ? `M ${curr.x} ${curr.y}` : `${acc} L ${curr.x} ${curr.y}`;
  }, "");

  // Color stroke by trajectory
  let strokeColor = "#0284c7"; // sky
  let fillColor = "rgba(2, 132, 199, 0.08)";
  if (trajectory === "IMPROVING") {
    strokeColor = "#059669"; // emerald
    fillColor = "rgba(5, 150, 105, 0.08)";
  } else if (trajectory === "CRITICAL_ATTENTION") {
    strokeColor = "#e11d48"; // rose
    fillColor = "rgba(225, 29, 72, 0.08)";
  } else if (trajectory === "DETERIORATING") {
    strokeColor = "#d97706"; // amber
    fillColor = "rgba(217, 119, 6, 0.08)";
  }

  return (
    <div className="relative">
      <div className="w-full overflow-hidden bg-slate-50/70 border border-slate-100 rounded-lg p-2">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-24 overflow-visible"
        >
          <defs>
            <linearGradient id={`grad-${trajectory}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity="0.25" />
              <stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Reference range guideline if multiple points */}
          <line
            x1={padX}
            y1={height / 2}
            x2={width - padX}
            y2={height / 2}
            stroke="#cbd5e1"
            strokeDasharray="3 3"
            strokeWidth="1"
          />

          {/* Fill under the curve */}
          {points.length > 1 && (
            <path
              d={`${pathD} L ${coords[coords.length - 1].x} ${height - padY} L ${coords[0].x} ${height - padY} Z`}
              fill={`url(#grad-${trajectory})`}
            />
          )}

          {/* Main trajectory stroke */}
          <path
            d={pathD}
            fill="none"
            stroke={strokeColor}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data Points */}
          {coords.map(({ x, y, pt }, idx) => (
            <g key={idx} className="cursor-pointer" onMouseEnter={() => setActivePoint(pt)} onMouseLeave={() => setActivePoint(null)}>
              <circle
                cx={x}
                cy={y}
                r={pt.is_critical ? 5.5 : pt.is_abnormal ? 4.5 : 3.5}
                fill={pt.is_critical ? "#e11d48" : pt.is_abnormal ? "#d97706" : strokeColor}
                stroke="#ffffff"
                strokeWidth="2"
                className="transition-all hover:scale-125"
              />
            </g>
          ))}
        </svg>

        {/* Date and Values Range footer */}
        <div className="flex justify-between items-center text-[11px] text-slate-400 mt-1 px-1">
          <span>{points[0].date.split("T")[0]}</span>
          <span className="font-mono text-slate-500 text-[10px]">
            Ref: {refInterval || "Standard bounds"}
          </span>
          <span>{points[points.length - 1].date.split("T")[0]}</span>
        </div>
      </div>

      {/* Hover Info Tooltip */}
      {activePoint && (
        <div className="absolute top-0 right-2 bg-slate-900 text-white text-[11px] px-2.5 py-1.5 rounded shadow-lg pointer-events-none z-10 animate-in fade-in duration-150">
          <div className="font-semibold">{activePoint.record_title}</div>
          <div className="text-slate-300">
            {activePoint.date.split("T")[0]}: <span className="font-mono text-emerald-400 font-bold">{activePoint.value.toLocaleString()} {unit}</span>
          </div>
          <div className="text-[10px] text-slate-400">
            Status: {activePoint.status}
          </div>
        </div>
      )}
    </div>
  );
}

export function PatientHistoryDashboard() {
  const { language } = useLanguage();
  const isSi = language === "si";

  // Data State
  const [profiles, setProfiles] = useState<PatientProfileItem[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string>("");
  const [currentProfile, setCurrentProfile] = useState<PatientProfileItem | null>(null);
  const [records, setRecords] = useState<PatientMedicalRecordItem[]>([]);
  const [trends, setTrends] = useState<PatientTrendsResponse | null>(null);
  const [recordFilter, setRecordFilter] = useState<string>("ALL");

  // Loading & Action State
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [showNewProfileModal, setShowNewProfileModal] = useState<boolean>(false);
  const [showAddRecordModal, setShowAddRecordModal] = useState<boolean>(false);
  const [notification, setNotification] = useState<{ text: string; isError?: boolean } | null>(null);

  // New Profile Form State
  const [newProfileForm, setNewProfileForm] = useState({
    first_name: "",
    last_name: "",
    relationship: "SELF",
    date_of_birth: "1995-01-01",
    biological_sex: "MALE",
    blood_group: "O+",
    allergies: "",
    chronic_conditions: "",
    emergency_contact_phone: "",
    notes: ""
  });

  // New Record Form State
  const [newRecordForm, setNewRecordForm] = useState({
    record_type: "LAB_REPORT",
    title: "",
    overall_status: "ALL_NORMAL",
    qualitative_verdict: "NOT_APPLICABLE",
    biomarker_name: "platelets",
    biomarker_value: "",
    biomarker_unit: "/uL",
    notes: ""
  });

  // Fetch all profiles on mount
  const loadProfiles = async () => {
    try {
      setLoading(true);
      const data = await fetchPatientProfiles();
      setProfiles(data);
      if (data.length > 0 && !selectedProfileId) {
        setSelectedProfileId(data[0].id);
      }
    } catch (err: any) {
      setNotification({ text: err.message || "Failed to load patient profiles", isError: true });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  // Fetch selected profile details, records, and longitudinal trends
  const loadProfileData = async (profId: string) => {
    if (!profId) return;
    try {
      setActionLoading(true);
      const [profileData, recordsData, trendsData] = await Promise.all([
        fetchPatientProfile(profId),
        fetchPatientRecords(profId),
        fetchPatientTrends(profId)
      ]);
      setCurrentProfile(profileData);
      setRecords(recordsData.records || []);
      setTrends(trendsData);
    } catch (err: any) {
      setNotification({ text: err.message || "Failed to load patient records", isError: true });
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    if (selectedProfileId) {
      loadProfileData(selectedProfileId);
    }
  }, [selectedProfileId]);

  // Handle Create Profile
  const handleCreateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProfileForm.first_name || !newProfileForm.last_name) return;

    try {
      setActionLoading(true);
      const allergiesList = newProfileForm.allergies
        ? newProfileForm.allergies.split(",").map((s) => s.trim()).filter(Boolean)
        : [];
      const chronicList = newProfileForm.chronic_conditions
        ? newProfileForm.chronic_conditions.split(",").map((s) => s.trim()).filter(Boolean)
        : [];

      const res = await createPatientProfile({
        first_name: newProfileForm.first_name,
        last_name: newProfileForm.last_name,
        relationship: newProfileForm.relationship,
        date_of_birth: newProfileForm.date_of_birth,
        biological_sex: newProfileForm.biological_sex,
        blood_group: newProfileForm.blood_group,
        allergies: allergiesList,
        chronic_conditions: chronicList,
        emergency_contact_phone: newProfileForm.emergency_contact_phone,
        notes: newProfileForm.notes
      });

      setShowNewProfileModal(false);
      setNotification({ text: isSi ? res.message_si : res.message_en });
      await loadProfiles();
      setSelectedProfileId(res.profile_id);
    } catch (err: any) {
      setNotification({ text: err.message || "Profile creation failed", isError: true });
    } finally {
      setActionLoading(false);
    }
  };

  // Handle Add Record
  const handleAddRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProfileId || !newRecordForm.title) return;

    try {
      setActionLoading(true);
      const biomarkersList: any[] = [];
      if (newRecordForm.biomarker_name && newRecordForm.biomarker_value) {
        const numVal = parseFloat(newRecordForm.biomarker_value);
        biomarkersList.push({
          canonical_id: newRecordForm.biomarker_name.toLowerCase(),
          display_name_en: newRecordForm.biomarker_name.toUpperCase(),
          display_name_si: newRecordForm.biomarker_name,
          category: "General",
          raw_value: newRecordForm.biomarker_value,
          numeric_value: isNaN(numVal) ? null : numVal,
          unit: newRecordForm.biomarker_unit,
          ref_interval: "",
          status: "RECORDED",
          status_si: "සටහන් කර ඇත",
          is_abnormal: false,
          is_critical: false
        });
      }

      const res = await createPatientRecord(selectedProfileId, {
        record_type: newRecordForm.record_type,
        title: newRecordForm.title,
        overall_status: newRecordForm.overall_status,
        qualitative_verdict: newRecordForm.qualitative_verdict,
        extracted_biomarkers: biomarkersList,
        correlated_icd11: [],
        notes: newRecordForm.notes
      });

      setShowAddRecordModal(false);
      setNotification({ text: isSi ? res.message_si : res.message_en });
      setNewRecordForm({
        record_type: "LAB_REPORT",
        title: "",
        overall_status: "ALL_NORMAL",
        qualitative_verdict: "NOT_APPLICABLE",
        biomarker_name: "platelets",
        biomarker_value: "",
        biomarker_unit: "/uL",
        notes: ""
      });
      await loadProfileData(selectedProfileId);
    } catch (err: any) {
      setNotification({ text: err.message || "Failed to append record", isError: true });
    } finally {
      setActionLoading(false);
    }
  };

  // Filtered records
  const filteredRecords = useMemo(() => {
    if (recordFilter === "ALL") return records;
    return records.filter((r) => r.record_type === recordFilter);
  }, [records, recordFilter]);

  const patientAge = calculateAge(currentProfile?.date_of_birth);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Toast Notification */}
      {notification && (
        <div
          className={`p-3.5 rounded-lg text-xs font-medium flex items-center justify-between border ${
            notification.isError
              ? "bg-rose-50 text-rose-800 border-rose-200"
              : "bg-emerald-50 text-emerald-800 border-emerald-200"
          }`}
        >
          <div className="flex items-center space-x-2">
            {notification.isError ? (
              <AlertCircle className="w-4 h-4 text-rose-600" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            )}
            <span>{notification.text}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Header & Profile Switcher Ribbon */}
      <div className="bg-white border border-[#CBE2EA] rounded-2xl overflow-hidden shadow-clinical-card">
        <div className="clinical-dark-preserve px-5 py-4 bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D7490] flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-teal-500/30">
          <div className="flex items-start gap-3">
            <span className="w-10 h-10 bg-white/10 border border-teal-300/30 text-teal-300 rounded-xl flex items-center justify-center shrink-0">
              <Activity className="w-5 h-5" />
            </span>
            <div>
              <h1 className="text-base sm:text-lg font-bold tracking-tight text-white">
                {isSi
                  ? "රෝගී සෞඛ්‍ය ඉතිහාසය සහ ප්‍රවණතා විශ්ලේෂණය"
                  : "Longitudinal Health Records & Biomarker Trends"}
              </h1>
              <p className="text-xs text-cyan-100/80 mt-0.5">
                {isSi
                  ? "පවුලේ සාමාජිකයන්ගේ රසායනාගාර වාර්තා, ඩෙංගු පට්ටිකා හෝ රුධිර සීනි ප්‍රවණතා සහ අඛණ්ඩ EHR ඉතිහාසය."
                  : "Multi-profile longitudinal EHR tracking with mathematical trajectory tracking across verified clinical biomarkers."}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => loadProfileData(selectedProfileId)}
              disabled={actionLoading}
              className="inline-flex items-center px-3 py-1.5 text-xs font-semibold text-cyan-100 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl transition-colors cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${actionLoading ? "animate-spin" : ""}`} />
              {isSi ? "යාවත්කාලීන" : "Refresh"}
            </button>
            <button
              onClick={() => setShowAddRecordModal(true)}
              className="inline-flex items-center px-3.5 py-1.5 text-xs font-bold text-white bg-teal-500 hover:bg-teal-400 rounded-xl transition-colors shadow-sm cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5 mr-1" />
              {isSi ? "නව වාර්තාවක්" : "Add Record"}
            </button>
            <button
              onClick={() => setShowNewProfileModal(true)}
              className="inline-flex items-center px-3.5 py-1.5 text-xs font-bold text-white bg-white/15 hover:bg-white/25 rounded-xl transition-colors border border-white/25 cursor-pointer"
            >
              <User className="w-3.5 h-3.5 mr-1" />
              {isSi ? "නව සාමාජිකයෙක්" : "New Profile"}
            </button>
          </div>
        </div>

        {/* Family Member Profile Pills */}
        <div className="p-4 bg-[#F4FAFC] flex items-center space-x-2 overflow-x-auto scrollbar-none">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap mr-1">
            {isSi ? "සාමාජිකයා:" : "Profiles:"}
          </span>
          {profiles.length === 0 && !loading ? (
            <button
              onClick={() => setShowNewProfileModal(true)}
              className="inline-flex items-center px-3.5 py-1.5 rounded-lg text-xs font-bold bg-teal-600 text-white hover:bg-teal-500 transition-colors cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5 mr-1.5" />
              {isSi ? "පළමු රෝගී ගිණුම සාදන්න (Create First Patient Profile)" : "Create First Patient Profile"}
            </button>
          ) : (
            profiles.map((p) => {
              const isSelected = p.id === selectedProfileId;
              return (
                <button
                  key={p.id}
                  onClick={() => setSelectedProfileId(p.id)}
                  className={`inline-flex items-center px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap border ${
                    isSelected
                      ? "bg-clinical-navy text-white border-clinical-navy shadow-xs ring-2 ring-clinical-navy/20"
                      : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100 hover:border-slate-300"
                  }`}
                >
                  <span className="w-2 h-2 rounded-full mr-2 bg-emerald-400" />
                  {p.full_name}
                  <span
                    className={`ml-2 px-1.5 py-0.2 rounded text-[10px] font-mono uppercase ${
                      isSelected ? "bg-white/20 text-white" : "bg-slate-200 text-slate-600"
                    }`}
                  >
                    {p.relationship}
                  </span>
                  <span className="ml-1.5 text-[10px] opacity-75">
                    ({p.total_records})
                  </span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Empty State when no Patient Profiles exist */}
      {profiles.length === 0 && !loading && (
        <div className="bg-white border border-[#CBE2EA] rounded-2xl p-8 text-center shadow-clinical-card">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-teal-50 border border-teal-200 text-teal-600 flex items-center justify-center mb-3">
            <Users className="w-7 h-7" />
          </div>
          <h2 className="text-base sm:text-lg font-extrabold text-[#0A2540]">
            {isSi
              ? "තවමත් රෝගී ගිණුම් ඇතුළත් කර නොමැත"
              : "No Patient Profiles Registered Yet"}
          </h2>
          <p className="text-xs text-slate-600 max-w-lg mx-auto mt-1.5 leading-relaxed">
            {isSi
              ? "ඔබගේ හෝ පවුලේ සාමාජිකයන්ගේ රසායනාගාර වාර්තා සහ සෞඛ්‍ය ප්‍රවණතා (Biomarker Trends) ආරක්ෂිතව සටහන් කර ගැනීමට නව රෝගී ගිණුමක් ආරම්භ කරන්න."
              : "Create your first patient or family member profile to securely store lab reports, track longitudinal biomarker trajectories, and manage clinical history."}
          </p>
          <button
            onClick={() => setShowNewProfileModal(true)}
            className="mt-4 inline-flex items-center px-5 py-2.5 rounded-xl text-xs font-extrabold text-white bg-gradient-to-r from-[#0D9488] to-[#0284C7] hover:from-[#0F766E] hover:to-[#0369A1] shadow-md transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            {isSi ? "නව රෝගී ගිණුමක් එක් කරන්න" : "Register First Patient Profile"}
          </button>
        </div>
      )}

      {/* Selected Patient Demographic & Summary Card */}
      {currentProfile && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-3">
                <div className="w-11 h-11 rounded-full bg-clinical-teal-light text-clinical-teal flex items-center justify-center font-bold text-base border border-clinical-teal-border">
                  {currentProfile.first_name[0]}{currentProfile.last_name[0]}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-lg font-bold text-clinical-navy">
                      {currentProfile.full_name}
                    </h2>
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                      {currentProfile.relationship}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                      {currentProfile.blood_group}
                    </span>
                  </div>
                  <div className="text-xs text-clinical-muted flex items-center space-x-3 mt-0.5">
                    {patientAge !== null && <span>{patientAge} {isSi ? "වයස" : "years old"}</span>}
                    <span>•</span>
                    <span>{currentProfile.biological_sex}</span>
                    {currentProfile.emergency_contact_phone && (
                      <>
                        <span>•</span>
                        <span className="inline-flex items-center text-slate-600">
                          <Phone className="w-3 h-3 mr-1 text-slate-400" />
                          {currentProfile.emergency_contact_phone}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="flex items-center space-x-4 bg-slate-50 border border-slate-200 rounded-lg p-3">
              <div className="text-center px-3 border-r border-slate-200">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                  {isSi ? "සම්පූර්ණ වාර්තා" : "Total Records"}
                </span>
                <span className="text-lg font-bold text-clinical-navy font-mono">
                  {records.length}
                </span>
              </div>
              <div className="text-center px-3">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                  {isSi ? "නිරීක්ෂිත දර්ශක" : "Tracked Biomarkers"}
                </span>
                <span className="text-lg font-bold text-clinical-teal font-mono">
                  {trends?.tracked_biomarkers_count || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Allergies and Chronic Conditions */}
          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div>
              <span className="font-semibold text-slate-700 block mb-1">
                {isSi ? "ඖෂධ සහ ආහාර ආසාත්මිකතා (Allergies):" : "Known Allergies:"}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {currentProfile.allergies && currentProfile.allergies.length > 0 ? (
                  currentProfile.allergies.map((all, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-800 border border-amber-200"
                    >
                      <ShieldAlert className="w-3 h-3 mr-1 text-amber-600" />
                      {all}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 text-xs italic">
                    {isSi ? "සටහන් කර නොමැත" : "No known adverse allergies recorded"}
                  </span>
                )}
              </div>
            </div>

            <div>
              <span className="font-semibold text-slate-700 block mb-1">
                {isSi ? "නිදන්ගත රෝග තත්ත්වයන් (Chronic Conditions):" : "Chronic Conditions:"}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {currentProfile.chronic_conditions && currentProfile.chronic_conditions.length > 0 ? (
                  currentProfile.chronic_conditions.map((cond, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-indigo-50 text-indigo-800 border border-indigo-200"
                    >
                      {cond}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 text-xs italic">
                    {isSi ? "නිදන්ගත රෝග වාර්තා වී නැත" : "No chronic pathology history documented"}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Longitudinal Trajectory Intelligence Summary */}
      {trends && trends.trends && trends.trends.length > 0 && (
        <div
          className={`border rounded-xl p-4 sm:p-5 shadow-xs ${
            trends.overall_trajectory === "IMPROVING"
              ? "bg-emerald-50/50 border-emerald-200"
              : trends.overall_trajectory === "CRITICAL_ATTENTION"
              ? "bg-rose-50/50 border-rose-200"
              : trends.overall_trajectory === "DETERIORATING"
              ? "bg-amber-50/50 border-amber-200"
              : "bg-sky-50/50 border-sky-200"
          }`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <span
                className={`p-2 rounded-lg ${
                  trends.overall_trajectory === "IMPROVING"
                    ? "bg-emerald-100 text-emerald-800"
                    : trends.overall_trajectory === "CRITICAL_ATTENTION"
                    ? "bg-rose-100 text-rose-800"
                    : trends.overall_trajectory === "DETERIORATING"
                    ? "bg-amber-100 text-amber-800"
                    : "bg-sky-100 text-sky-800"
                }`}
              >
                {trends.overall_trajectory === "IMPROVING" ? (
                  <TrendingUp className="w-5 h-5 text-emerald-700" />
                ) : trends.overall_trajectory === "CRITICAL_ATTENTION" ? (
                  <ShieldAlert className="w-5 h-5 text-rose-700" />
                ) : trends.overall_trajectory === "DETERIORATING" ? (
                  <TrendingDown className="w-5 h-5 text-amber-700" />
                ) : (
                  <Minus className="w-5 h-5 text-sky-700" />
                )}
              </span>
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block">
                  {isSi ? "සමස්ත සායනික ප්‍රවණතාවය (Longitudinal Trajectory)" : "Overall Clinical Trajectory"}
                </span>
                <span className="text-base font-bold text-clinical-navy">
                  {trends.overall_trajectory}
                </span>
              </div>
            </div>

            <div className="text-xs text-slate-600 max-w-xl">
              {isSi ? trends.longitudinal_summary_si : trends.longitudinal_summary_en}
            </div>
          </div>
        </div>
      )}

      {/* Biomarker Trend Cards Grid */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-clinical-teal" />
            <h3 className="text-sm font-bold text-clinical-navy uppercase tracking-wider">
              {isSi ? "ජෛව සලකුණු ප්‍රවණතා විශ්ලේෂණය" : "Biomarker Trend Trajectories"}
            </h3>
            <span className="text-xs text-slate-400">
              ({trends?.trends?.length || 0} {isSi ? "දර්ශක" : "parameters"})
            </span>
          </div>
        </div>

        {trends && trends.trends && trends.trends.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trends.trends.map((trend: BiomarkerTrendItem) => {
              const isImproving = trend.trajectory === "IMPROVING";
              const isCritical = trend.trajectory === "CRITICAL_ATTENTION" || trend.is_critical;
              const isDeteriorating = trend.trajectory === "DETERIORATING";

              const badgeColor = isImproving
                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                : isCritical
                ? "bg-rose-50 text-rose-700 border-rose-200 animate-pulse"
                : isDeteriorating
                ? "bg-amber-50 text-amber-700 border-amber-200"
                : "bg-sky-50 text-sky-700 border-sky-200";

              return (
                <div
                  key={trend.canonical_id}
                  className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs hover:shadow-sm transition-all flex flex-col justify-between"
                >
                  <div>
                    {/* Top Row: Biomarker name & Trajectory Badge */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <span className="text-[10px] font-mono uppercase text-slate-400 block">
                          {trend.category}
                        </span>
                        <h4 className="text-sm font-bold text-clinical-navy leading-snug">
                          {trend.display_name_en}
                        </h4>
                        <span className="text-xs text-clinical-muted block">
                          {trend.display_name_si}
                        </span>
                      </div>

                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border whitespace-nowrap ${badgeColor}`}
                      >
                        {trend.trajectory}
                      </span>
                    </div>

                    {/* Value Metrics & Delta */}
                    <div className="flex items-baseline justify-between mt-3 mb-2">
                      <div>
                        <span className="text-2xl font-bold font-mono text-clinical-navy">
                          {trend.latest_value.toLocaleString()}
                        </span>
                        <span className="text-xs text-slate-500 ml-1.5 font-medium">
                          {trend.unit}
                        </span>
                      </div>

                      <div className="text-right">
                        <span
                          className={`inline-flex items-center text-xs font-bold font-mono ${
                            trend.delta_value > 0
                              ? "text-emerald-600"
                              : trend.delta_value < 0
                              ? "text-rose-600"
                              : "text-slate-500"
                          }`}
                        >
                          {trend.delta_value > 0 ? (
                            <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
                          ) : trend.delta_value < 0 ? (
                            <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
                          ) : (
                            <Minus className="w-3.5 h-3.5 mr-0.5" />
                          )}
                          {trend.delta_value > 0 ? `+${trend.delta_value.toLocaleString()}` : trend.delta_value.toLocaleString()}
                          {trend.delta_percentage !== 0 && (
                            <span className="text-[10px] ml-1">
                              ({trend.delta_percentage > 0 ? `+${trend.delta_percentage}` : trend.delta_percentage}%)
                            </span>
                          )}
                        </span>
                        <span className="text-[10px] text-slate-400 block">
                          vs previous
                        </span>
                      </div>
                    </div>

                    {/* SVG Sparkline */}
                    <div className="my-2">
                      <BiomarkerSparkline
                        points={trend.data_points}
                        trajectory={trend.trajectory}
                        unit={trend.unit}
                        refInterval={trend.ref_interval}
                      />
                    </div>
                  </div>

                  {/* Clinical Directives */}
                  <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-600 space-y-1 mt-2">
                    <div className="font-semibold text-slate-700">
                      {isSi ? trend.trajectory_label_si : trend.trajectory_label_en}
                    </div>
                    <div className="text-slate-500 text-[10px] leading-relaxed">
                      {isSi ? trend.clinical_insight_si : trend.clinical_insight_en}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-500">
            <Activity className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="text-xs">
              {isSi
                ? "මෙම රෝගියා සඳහා ප්‍රමාණවත් රසායනාගාර දත්ත නොමැත. කරුණාකර නව වාර්තාවක් එක් කරන්න."
                : "No quantitative biomarker series recorded yet. Upload a lab report or manually add measurements to track trends."}
            </p>
          </div>
        )}
      </div>

      {/* Chronological Medical Records Timeline Stream */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
          <div>
            <h3 className="text-sm font-bold text-clinical-navy uppercase tracking-wider">
              {isSi ? "කාලානුක්‍රමික සෞඛ්‍ය වාර්තා ඉතිහාසය" : "Chronological Medical Records Stream"}
            </h3>
            <span className="text-xs text-clinical-muted">
              {isSi
                ? "සියලුම රසායනාගාර පරීක්ෂණ, Triage විමසීම් සහ සායනික සටහන්."
                : "Sequential repository of diagnostic lab reports, triage assessments, and clinical documentation."}
            </span>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg text-xs">
            {["ALL", "LAB_REPORT", "TRIAGE_SESSION", "DISCHARGE_SUMMARY"].map((f) => (
              <button
                key={f}
                onClick={() => setRecordFilter(f)}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  recordFilter === f
                    ? "bg-white text-clinical-navy font-bold shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {f === "ALL"
                  ? isSi ? "සියල්ල" : "All"
                  : f === "LAB_REPORT"
                  ? isSi ? "රසායනාගාර" : "Labs"
                  : f === "TRIAGE_SESSION"
                  ? "Triage"
                  : isSi ? "සාරාංශ" : "Discharge"}
              </button>
            ))}
          </div>
        </div>

        {/* Timeline Items */}
        {filteredRecords.length > 0 ? (
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
            {filteredRecords.map((rec) => {
              const isAbnormal = rec.overall_status === "ABNORMAL_ELEVATED_RISK";
              const isEmergency = rec.overall_status === "CRITICAL_EMERGENCY";

              return (
                <div key={rec.id} className="relative group">
                  {/* Timeline circle icon */}
                  <span
                    className={`absolute -left-6 top-1.5 w-5 h-5 rounded-full border-2 border-white flex items-center justify-center text-[10px] ${
                      isEmergency
                        ? "bg-rose-500 text-white"
                        : isAbnormal
                        ? "bg-amber-500 text-white"
                        : "bg-emerald-500 text-white"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-white" />
                  </span>

                  <div className="bg-slate-50/70 border border-slate-200 rounded-lg p-4 hover:border-slate-300 transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-slate-200 text-slate-700">
                            {rec.record_type}
                          </span>
                          <h4 className="text-sm font-bold text-clinical-navy">
                            {rec.title}
                          </h4>
                        </div>
                        <span className="text-xs text-slate-400 flex items-center space-x-1 mt-0.5">
                          <Calendar className="w-3 h-3 text-slate-400" />
                          <span>{rec.record_date.replace("T", " ").substring(0, 16)}</span>
                          {rec.source_filename && (
                            <>
                              <span>•</span>
                              <span className="font-mono text-[10px]">{rec.source_filename}</span>
                            </>
                          )}
                        </span>
                      </div>

                      <div className="flex items-center space-x-2">
                        {rec.qualitative_verdict && rec.qualitative_verdict !== "NOT_APPLICABLE" && (
                          <span
                            className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                              rec.qualitative_verdict === "POSITIVE"
                                ? "bg-rose-100 text-rose-800 border border-rose-300"
                                : "bg-emerald-100 text-emerald-800 border border-emerald-300"
                            }`}
                          >
                            {rec.qualitative_verdict}
                          </span>
                        )}
                        <span
                          className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                            isEmergency
                              ? "bg-rose-100 text-rose-800"
                              : isAbnormal
                              ? "bg-amber-100 text-amber-800"
                              : "bg-emerald-100 text-emerald-800"
                          }`}
                        >
                          {rec.overall_status}
                        </span>
                      </div>
                    </div>

                    {/* Extracted Biomarkers Pills */}
                    {rec.extracted_biomarkers && rec.extracted_biomarkers.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-slate-200/60">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                          {isSi ? "වාර්තාගත අගයන්:" : "Extracted Laboratory Values:"}
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {rec.extracted_biomarkers.map((b: any, bIdx: number) => (
                            <div
                              key={bIdx}
                              className={`px-2.5 py-1 rounded text-xs border font-mono flex items-center space-x-2 ${
                                b.is_critical
                                  ? "bg-rose-50 border-rose-300 text-rose-900"
                                  : b.is_abnormal
                                  ? "bg-amber-50 border-amber-300 text-amber-900"
                                  : "bg-white border-slate-200 text-slate-800"
                              }`}
                            >
                              <span className="font-sans font-semibold">
                                {isSi ? b.display_name_si || b.canonical_id : b.display_name_en || b.canonical_id}:
                              </span>
                              <span className="font-bold">
                                {b.numeric_value !== null ? b.numeric_value.toLocaleString() : b.raw_value} {b.unit}
                              </span>
                              {b.status && (
                                <span className="text-[9px] px-1 py-0.2 rounded bg-slate-100 text-slate-600">
                                  {b.status}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Correlated ICD-11 */}
                    {rec.correlated_icd11 && rec.correlated_icd11.length > 0 && (
                      <div className="mt-2 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] text-slate-400 uppercase font-semibold">ICD-11:</span>
                        {rec.correlated_icd11.map((icd: any, icdIdx: number) => (
                          <span
                            key={icdIdx}
                            className="px-2 py-0.5 rounded text-[10px] bg-slate-200 text-slate-800 font-mono font-medium"
                          >
                            {icd.icd11 || icd.code} - {icd.condition || icd.name}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Notes */}
                    {rec.notes && (
                      <div className="mt-2 text-xs text-slate-600 bg-white p-2 rounded border border-slate-200/80">
                        <span className="font-semibold text-slate-700 mr-1">{isSi ? "සායනික සටහන:" : "Clinical Notes:"}</span>
                        {rec.notes}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-400 text-xs">
            {isSi ? "වාර්තා සටහන් කිසිවක් නැත." : "No records match this filter."}
          </div>
        )}
      </div>

      {/* Modal: Add New Profile */}
      {showNewProfileModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-clinical-navy">
                {isSi ? "නව පවුලේ සාමාජිකයෙකු එක් කරන්න" : "Add Family Member Patient Profile"}
              </h3>
              <button
                onClick={() => setShowNewProfileModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateProfile} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "මුල් නම" : "First Name"} *
                  </label>
                  <input
                    type="text"
                    required
                    value={newProfileForm.first_name}
                    onChange={(e) =>
                      setNewProfileForm({ ...newProfileForm, first_name: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-1 focus:ring-clinical-teal focus:border-clinical-teal"
                    placeholder="e.g. John"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "වාසගම" : "Last Name"} *
                  </label>
                  <input
                    type="text"
                    required
                    value={newProfileForm.last_name}
                    onChange={(e) =>
                      setNewProfileForm({ ...newProfileForm, last_name: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-1 focus:ring-clinical-teal focus:border-clinical-teal"
                    placeholder="e.g. Doe"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "සම්බන්ධතාවය" : "Relationship"}
                  </label>
                  <select
                    value={newProfileForm.relationship}
                    onChange={(e) =>
                      setNewProfileForm({ ...newProfileForm, relationship: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs"
                  >
                    <option value="SELF">SELF</option>
                    <option value="FATHER">FATHER</option>
                    <option value="MOTHER">MOTHER</option>
                    <option value="SPOUSE">SPOUSE</option>
                    <option value="CHILD">CHILD</option>
                    <option value="SIBLING">SIBLING</option>
                    <option value="OTHER">OTHER</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "ස්ත්‍රී / පුරුෂ භාවය" : "Sex"}
                  </label>
                  <select
                    value={newProfileForm.biological_sex}
                    onChange={(e) =>
                      setNewProfileForm({ ...newProfileForm, biological_sex: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs"
                  >
                    <option value="MALE">MALE</option>
                    <option value="FEMALE">FEMALE</option>
                    <option value="UNSPECIFIED">UNSPECIFIED</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "රුධිර කාණ්ඩය" : "Blood Group"}
                  </label>
                  <select
                    value={newProfileForm.blood_group}
                    onChange={(e) =>
                      setNewProfileForm({ ...newProfileForm, blood_group: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs"
                  >
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="UNKNOWN">UNKNOWN</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "උපන් දිනය" : "Date of Birth (YYYY-MM-DD)"}
                </label>
                <input
                  type="date"
                  value={newProfileForm.date_of_birth}
                  onChange={(e) =>
                    setNewProfileForm({ ...newProfileForm, date_of_birth: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "ආසාත්මිකතා (කොමා මඟින් වෙන් කරන්න)" : "Allergies (comma-separated)"}
                </label>
                <input
                  type="text"
                  value={newProfileForm.allergies}
                  onChange={(e) =>
                    setNewProfileForm({ ...newProfileForm, allergies: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                  placeholder="e.g. Penicillin, Aspirin"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "නිදන්ගත රෝග (කොමා මඟින් වෙන් කරන්න)" : "Chronic Conditions (comma-separated)"}
                </label>
                <input
                  type="text"
                  value={newProfileForm.chronic_conditions}
                  onChange={(e) =>
                    setNewProfileForm({ ...newProfileForm, chronic_conditions: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                  placeholder="e.g. Type 2 Diabetes, Hypertension"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "හදිසි ඇමතුම් අංකය" : "Emergency Contact Phone"}
                </label>
                <input
                  type="text"
                  value={newProfileForm.emergency_contact_phone}
                  onChange={(e) =>
                    setNewProfileForm({
                      ...newProfileForm,
                      emergency_contact_phone: e.target.value
                    })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                  placeholder="+94 77 123 4567"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "අමතර සායනික සටහන්" : "Clinical Notes"}
                </label>
                <textarea
                  rows={2}
                  value={newProfileForm.notes}
                  onChange={(e) =>
                    setNewProfileForm({ ...newProfileForm, notes: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                  placeholder="e.g. Regular medication schedule..."
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowNewProfileModal(false)}
                  className="px-3 py-2 rounded-lg text-slate-600 bg-slate-100 hover:bg-slate-200"
                >
                  {isSi ? "අවලංගු කරන්න" : "Cancel"}
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 rounded-lg font-semibold text-white bg-clinical-teal hover:bg-clinical-teal-dark shadow-xs"
                >
                  {actionLoading
                    ? isSi ? "සුරකිමින්..." : "Saving..."
                    : isSi ? "පැතිකඩ සාදන්න" : "Create Profile"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Add Medical Record */}
      {showAddRecordModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-clinical-navy">
                {isSi ? "නව වෛද්‍ය වාර්තාවක් එක් කරන්න" : "Append Medical Record to EHR"}
              </h3>
              <button
                onClick={() => setShowAddRecordModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddRecord} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "වාර්තා වර්ගය" : "Record Type"}
                </label>
                <select
                  value={newRecordForm.record_type}
                  onChange={(e) =>
                    setNewRecordForm({ ...newRecordForm, record_type: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs"
                >
                  <option value="LAB_REPORT">LAB_REPORT (Laboratory Test)</option>
                  <option value="TRIAGE_SESSION">TRIAGE_SESSION (Clinical Intake)</option>
                  <option value="PHYSICAL_EXAM">PHYSICAL_EXAM (Consultation)</option>
                  <option value="DISCHARGE_SUMMARY">DISCHARGE_SUMMARY (Hospitalization)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "වාර්තාවේ නම" : "Record Title"} *
                </label>
                <input
                  type="text"
                  required
                  value={newRecordForm.title}
                  onChange={(e) =>
                    setNewRecordForm({ ...newRecordForm, title: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                  placeholder="e.g. Day 4 FBC - Platelet Follow-up"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "සමස්ත තත්ත්වය" : "Overall Status"}
                  </label>
                  <select
                    value={newRecordForm.overall_status}
                    onChange={(e) =>
                      setNewRecordForm({ ...newRecordForm, overall_status: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs"
                  >
                    <option value="ALL_NORMAL">ALL_NORMAL</option>
                    <option value="ABNORMAL_ELEVATED_RISK">ABNORMAL_ELEVATED_RISK</option>
                    <option value="CRITICAL_EMERGENCY">CRITICAL_EMERGENCY</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    {isSi ? "තහවුරු කිරීම (Verdict)" : "Verdict"}
                  </label>
                  <select
                    value={newRecordForm.qualitative_verdict}
                    onChange={(e) =>
                      setNewRecordForm({ ...newRecordForm, qualitative_verdict: e.target.value })
                    }
                    className="w-full border border-slate-300 rounded-lg px-2.5 py-2 text-xs"
                  >
                    <option value="NOT_APPLICABLE">NOT_APPLICABLE</option>
                    <option value="POSITIVE">POSITIVE</option>
                    <option value="NEGATIVE">NEGATIVE</option>
                  </select>
                </div>
              </div>

              {/* Biomarker measurement entry */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-2">
                <span className="text-[11px] font-bold text-slate-700 block">
                  {isSi ? "ජෛව සලකුණු අගයක් (Biomarker Measurement):" : "Biomarker Measurement:"}
                </span>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-[10px] text-slate-500 mb-0.5">Biomarker</label>
                    <select
                      value={newRecordForm.biomarker_name}
                      onChange={(e) => {
                        const val = e.target.value;
                        let defaultUnit = "/uL";
                        if (val === "fasting_blood_sugar") defaultUnit = "mg/dL";
                        if (val === "hba1c") defaultUnit = "%";
                        if (val === "cholesterol_total") defaultUnit = "mg/dL";
                        if (val === "creatinine") defaultUnit = "mg/dL";
                        if (val === "hemoglobin") defaultUnit = "g/dL";
                        if (val === "pcv") defaultUnit = "%";
                        setNewRecordForm({
                          ...newRecordForm,
                          biomarker_name: val,
                          biomarker_unit: defaultUnit
                        });
                      }}
                      className="w-full border border-slate-300 rounded px-2 py-1 text-xs"
                    >
                      <option value="platelets">Platelets (Dengue)</option>
                      <option value="wbc">WBC (Leukocytes)</option>
                      <option value="fasting_blood_sugar">FBS (Blood Sugar)</option>
                      <option value="hba1c">HbA1c</option>
                      <option value="cholesterol_total">Total Cholesterol</option>
                      <option value="creatinine">Creatinine (Renal)</option>
                      <option value="hemoglobin">Hemoglobin (Hb)</option>
                      <option value="pcv">PCV (Hematocrit)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-500 mb-0.5">Value</label>
                    <input
                      type="number"
                      step="any"
                      value={newRecordForm.biomarker_value}
                      onChange={(e) =>
                        setNewRecordForm({ ...newRecordForm, biomarker_value: e.target.value })
                      }
                      className="w-full border border-slate-300 rounded px-2 py-1 text-xs"
                      placeholder="e.g. 110000"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-500 mb-0.5">Unit</label>
                    <input
                      type="text"
                      value={newRecordForm.biomarker_unit}
                      onChange={(e) =>
                        setNewRecordForm({ ...newRecordForm, biomarker_unit: e.target.value })
                      }
                      className="w-full border border-slate-300 rounded px-2 py-1 text-xs"
                      placeholder="/uL"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  {isSi ? "සටහන්" : "Notes / Clinical Findings"}
                </label>
                <textarea
                  rows={2}
                  value={newRecordForm.notes}
                  onChange={(e) =>
                    setNewRecordForm({ ...newRecordForm, notes: e.target.value })
                  }
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs"
                  placeholder="e.g. Vital signs stable, hydration maintained..."
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddRecordModal(false)}
                  className="px-3 py-2 rounded-lg text-slate-600 bg-slate-100 hover:bg-slate-200"
                >
                  {isSi ? "අවලංගු කරන්න" : "Cancel"}
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 rounded-lg font-semibold text-white bg-clinical-teal hover:bg-clinical-teal-dark shadow-xs"
                >
                  {actionLoading
                    ? isSi ? "සුරකිමින්..." : "Saving..."
                    : isSi ? "වාර්තාව එකතු කරන්න" : "Append Record"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

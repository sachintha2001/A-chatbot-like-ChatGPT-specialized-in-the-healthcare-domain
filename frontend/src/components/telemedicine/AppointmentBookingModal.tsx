"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Calendar,
  Clock,
  Building2,
  Video,
  CheckCircle2,
  ExternalLink,
  Stethoscope,
  ShieldAlert,
  PhoneCall,
  FileText,
  Copy,
  Check,
  Award,
  Sparkles,
  UserCheck
} from "lucide-react";
import {
  SpecialistDoctor,
  AppointmentBookingResponse
} from "@/lib/types";
import {
  recommendSpecialistsForPatient,
  bookSpecialistAppointment
} from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";

interface AppointmentBookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  specialtyHint?: string;
  clinicalContext?: string;
  triageAcuity?: string;
  icd11Codes?: string[];
  preselectedDoctor?: SpecialistDoctor | null;
  onBookingConfirmed?: (booking: AppointmentBookingResponse) => void;
}

export function AppointmentBookingModal({
  isOpen,
  onClose,
  specialtyHint,
  clinicalContext,
  triageAcuity = "ROUTINE",
  icd11Codes = [],
  preselectedDoctor = null,
  onBookingConfirmed
}: AppointmentBookingModalProps) {
  const { language } = useLanguage();
  const isSi = language === "si";

  const [loadingSpecialists, setLoadingSpecialists] = useState(false);
  const [matchedSpecialtyLabel, setMatchedSpecialtyLabel] = useState<string>("");
  const [emergencyWarning, setEmergencyWarning] = useState<string | null>(null);
  const [specialists, setSpecialists] = useState<SpecialistDoctor[]>([]);
  const [selectedDoctor, setSelectedDoctor] = useState<SpecialistDoctor | null>(null);

  const [bookingGateway, setBookingGateway] = useState<string>("ECHANNELLING");
  const [consultationMode, setConsultationMode] = useState<string>("IN_PERSON_HOSPITAL");
  const [selectedHospital, setSelectedHospital] = useState<string>("");
  const [selectedSlot, setSelectedSlot] = useState<string>("");

  const [patientName, setPatientName] = useState<string>("Kasun Perera");
  const [patientPhone, setPatientPhone] = useState<string>("0771234567");
  const [patientAge, setPatientAge] = useState<string>("38");
  const [clinicalSummary, setClinicalSummary] = useState<string>(clinicalContext || "");

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [confirmedBooking, setConfirmedBooking] = useState<AppointmentBookingResponse | null>(null);
  const [copiedSbar, setCopiedSbar] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setConfirmedBooking(null);
    setErrorMsg(null);
    setClinicalSummary(clinicalContext || "");

    if (preselectedDoctor) {
      setSpecialists([preselectedDoctor]);
      setSelectedDoctor(preselectedDoctor);
      setMatchedSpecialtyLabel(isSi ? preselectedDoctor.specialty_si : preselectedDoctor.specialty_en);
      setSelectedHospital(preselectedDoctor.primary_hospital_en);
      setSelectedSlot(preselectedDoctor.next_available_slots[0] || "Today • 05:00 PM");
      setConsultationMode(preselectedDoctor.supported_modes[0] || "IN_PERSON_HOSPITAL");
      setBookingGateway(preselectedDoctor.supported_gateways[0] || "ECHANNELLING");
      return;
    }

    setLoadingSpecialists(true);
    recommendSpecialistsForPatient({
      specialty_hint: specialtyHint,
      clinical_context: clinicalContext,
      triage_acuity: triageAcuity,
      icd11_codes: icd11Codes,
      language
    })
      .then((res) => {
        setSpecialists(res.specialists || []);
        setMatchedSpecialtyLabel(isSi ? res.matched_specialty_si : res.matched_specialty_en);
        setEmergencyWarning(
          res.emergency_warning_active
            ? (isSi ? res.emergency_directive_si || null : res.emergency_directive_en || null)
            : null
        );
        if (res.specialists && res.specialists.length > 0) {
          const first = res.specialists[0];
          setSelectedDoctor(first);
          setSelectedHospital(first.primary_hospital_en);
          setSelectedSlot(first.next_available_slots[0] || "Today • 05:00 PM");
          setConsultationMode(res.recommended_consultation_mode || first.supported_modes[0] || "IN_PERSON_HOSPITAL");
          setBookingGateway(first.supported_gateways[0] || "ECHANNELLING");
        }
      })
      .catch((err) => {
        setErrorMsg(err.message || "Failed to load recommended specialists");
      })
      .finally(() => {
        setLoadingSpecialists(false);
      });
  }, [isOpen, specialtyHint, clinicalContext, triageAcuity, preselectedDoctor, isSi, language]);

  if (!isOpen) return null;

  const handleSelectDoctor = (doc: SpecialistDoctor) => {
    setSelectedDoctor(doc);
    setSelectedHospital(doc.primary_hospital_en);
    setSelectedSlot(doc.next_available_slots[0] || "Today • 05:00 PM");
    if (!doc.supported_modes.includes(consultationMode)) {
      setConsultationMode(doc.supported_modes[0] || "IN_PERSON_HOSPITAL");
    }
    if (!doc.supported_gateways.includes(bookingGateway)) {
      setBookingGateway(doc.supported_gateways[0] || "ECHANNELLING");
    }
  };

  const handleConfirmBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoctor) return;
    if (!patientName.trim() || !patientPhone.trim()) {
      setErrorMsg(
        isSi
          ? "කරුණාකර රෝගියාගේ නම සහ දුරකථන අංකය ඇතුළත් කරන්න."
          : "Please enter patient full name and contact phone number."
      );
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);
    try {
      const result = await bookSpecialistAppointment({
        doctor_id: selectedDoctor.doctor_id,
        patient_name: patientName.trim(),
        patient_phone: patientPhone.trim(),
        patient_age: patientAge ? parseInt(patientAge, 10) : 38,
        preferred_slot: selectedSlot,
        consultation_mode: consultationMode,
        booking_gateway: bookingGateway,
        hospital_name: selectedHospital,
        clinical_context_summary: clinicalSummary,
        recommended_specialty: matchedSpecialtyLabel,
        triage_acuity: triageAcuity,
        correlated_icd11_codes: icd11Codes,
        language
      });
      setConfirmedBooking(result);
      onBookingConfirmed?.(result);
    } catch (err: any) {
      setErrorMsg(err.message || "Appointment booking failed");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopySbar = () => {
    if (!confirmedBooking) return;
    const text = isSi
      ? confirmedBooking.sbar_clinical_handover_si
      : confirmedBooking.sbar_clinical_handover_en;
    navigator.clipboard.writeText(text);
    setCopiedSbar(true);
    setTimeout(() => setCopiedSbar(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#0A2540]/65 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-[#CBE2EA] rounded-2xl max-w-3xl w-full shadow-clinical-elevated overflow-hidden my-6 max-h-[92vh] flex flex-col text-slate-100">
        {/* Modal Header */}
        <div className="clinical-dark-preserve px-6 py-4 bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D7490] border-b border-teal-500/30 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 border border-teal-300/30 flex items-center justify-center text-teal-300">
              <Stethoscope className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm sm:text-base font-bold text-white flex items-center gap-2">
                <span>
                  {isSi
                    ? "විශේෂඥ වෛද්‍ය හමුවක් වෙන්කරවා ගැනීම (eChannelling / Doc990 / oDoc)"
                    : "Specialist Doctor & Telemedicine Appointment Booking"}
                </span>
                <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-teal-400/20 text-teal-200 border border-teal-300/40">
                  SLMC Verified
                </span>
              </div>
              <div className="text-xs text-cyan-100/80">
                {matchedSpecialtyLabel
                  ? `${isSi ? "නිර්දේශිත වෛද්‍ය අංශය:" : "Matched Specialty:"} ${matchedSpecialtyLabel}`
                  : isSi
                  ? "ශ්‍රී ලංකාවේ ප්‍රමුඛ රෝහල් සහ වීඩියෝ වෛද්‍ය සේවා හරහා ක්ෂණික වෙන්කිරීම්"
                  : "Instant channelling across Sri Lankan Private Hospitals & 24/7 Telemedicine"}
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-cyan-100 hover:text-white border border-white/20 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>


        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Emergency Red-Flag Alert if Triage is EMERGENCY */}
          {emergencyWarning && (
            <div className="p-4 rounded-xl bg-rose-950/90 border border-rose-600 text-rose-100 flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <ShieldAlert className="w-6 h-6 text-rose-400 shrink-0 animate-pulse mt-0.5" />
                <div className="text-xs leading-relaxed">
                  <div className="font-bold uppercase tracking-wider text-rose-300 mb-0.5">
                    {isSi ? "හදිසි වෛද්‍ය අනතුරු ඇඟවීම" : "Emergency Acuity Override"}
                  </div>
                  {emergencyWarning}
                </div>
              </div>
              <a
                href="tel:1990"
                className="px-3.5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold flex items-center gap-1.5 shrink-0 shadow-md"
              >
                <PhoneCall className="w-3.5 h-3.5" />
                <span>1990 Suwa Seriya</span>
              </a>
            </div>
          )}

          {confirmedBooking ? (
            /* BOOKING CONFIRMATION & SBAR HANDOVER VIEW */
            <div className="space-y-5">
              <div className="p-5 rounded-2xl bg-emerald-950/60 border border-emerald-600/80 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0" />
                    <div>
                      <div className="text-[11px] font-mono uppercase tracking-wider text-emerald-300 font-bold">
                        {isSi ? "වෛද්‍ය හමුව තහවුරු කරන ලදී" : "Appointment Reservation Confirmed"}
                      </div>
                      <h3 className="text-base font-bold text-slate-100">
                        {isSi ? confirmedBooking.doctor.full_name_si : confirmedBooking.doctor.full_name_en}
                      </h3>
                      <p className="text-xs text-emerald-300">
                        {isSi ? confirmedBooking.doctor.specialty_si : confirmedBooking.doctor.specialty_en} •{" "}
                        {confirmedBooking.doctor.slmc_reg_no}
                      </p>
                    </div>
                  </div>
                  <div className="text-right font-mono">
                    <div className="text-[10px] text-emerald-300 uppercase">Booking Ref</div>
                    <div className="text-sm font-bold text-slate-100 bg-slate-950/80 px-2.5 py-1 rounded border border-emerald-600">
                      {confirmedBooking.booking_reference}
                    </div>
                  </div>

                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-emerald-800/60 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">
                      {isSi ? "ටෝකන් අංකය (Token)" : "Queue Token"}
                    </div>
                    <div className="text-sm font-bold text-teal-400 font-mono mt-0.5">
                      #{confirmedBooking.queue_token_number}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">
                      {isSi ? "වෙන්කළ වේලාව" : "Scheduled Slot"}
                    </div>
                    <div className="text-xs font-semibold text-slate-200 mt-0.5">
                      {confirmedBooking.scheduled_slot}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">
                      {isSi ? "රෝහල / ජාලය" : "Hospital / Gateway"}
                    </div>
                    <div className="text-xs font-semibold text-slate-200 mt-0.5 truncate">
                      {confirmedBooking.hospital_or_platform} ({confirmedBooking.booking_gateway})
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
                    <div className="text-[10px] text-slate-400 uppercase">
                      {isSi ? "වෛද්‍ය ගාස්තුව" : "Consultation Fee"}
                    </div>
                    <div className="text-xs font-bold text-emerald-300 font-mono mt-0.5">
                      LKR {confirmedBooking.estimated_fee_lkr.toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2.5 pt-2">
                  <a
                    href={confirmedBooking.external_gateway_redirect_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold shadow-md transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>
                      {isSi
                        ? `${confirmedBooking.booking_gateway} ද්වාරය විවෘත කරන්න`
                        : `Complete on ${confirmedBooking.booking_gateway} Portal`}
                    </span>
                  </a>

                  {confirmedBooking.telemedicine_meeting_url && (
                    <a
                      href={confirmedBooking.telemedicine_meeting_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md transition-colors"
                    >
                      <Video className="w-3.5 h-3.5" />
                      <span>
                        {isSi ? "සජීවී වීඩියෝ සායනයට සම්බන්ධ වන්න" : "Launch Telemedicine Video Room"}
                      </span>
                    </a>
                  )}
                </div>
              </div>

              {/* Automated SBAR Clinical Handover Note */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-1.5">
                    <FileText className="w-4 h-4" />
                    <span>
                      {isSi
                        ? "විශේෂඥ වෛද්‍යවරයා වෙත යැවෙන ස්වයංක්‍රීය සායනික වාර්තාව (SBAR Handover)"
                        : "Automated SBAR Clinical Handover Packet (Attached for Doctor)"}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleCopySbar}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium transition-colors"
                  >
                    {copiedSbar ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-300">{isSi ? "පිටපත් විය" : "Copied"}</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3 text-slate-400" />
                        <span>{isSi ? "වාර්තාව පිටපත් කරන්න" : "Copy SBAR Note"}</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {isSi
                    ? confirmedBooking.sbar_clinical_handover_si
                    : confirmedBooking.sbar_clinical_handover_en}
                </pre>
              </div>

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors"
                >
                  {isSi ? "වසන්න (Done)" : "Close Window"}
                </button>
              </div>
            </div>
          ) : loadingSpecialists ? (
            <div className="py-12 text-center space-y-3">
              <Stethoscope className="w-8 h-8 text-teal-400 animate-bounce mx-auto" />
              <div className="text-xs text-slate-400">
                {isSi
                  ? "ඔබගේ රෝග ලක්ෂණ සහ වාර්තාවට ගැළපෙන විශේෂඥ වෛද්‍යවරුන් සොයමින් පවතී..."
                  : "Matching SLMC-registered Specialists on eChannelling, Doc990 & oDoc..."}
              </div>
            </div>
          ) : (
            <form onSubmit={handleConfirmBooking} className="space-y-5">
              {/* Step 1: Select Matched Specialist Doctor */}
              <div className="space-y-2.5">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <UserCheck className="w-4 h-4 text-teal-400" />
                    <span>
                      {isSi
                        ? "1. නිර්දේශිත විශේෂඥ වෛද්‍යවරයා තෝරන්න"
                        : "1. Select Recommended Specialist Consultant"}
                    </span>
                  </span>
                  <span className="text-[11px] font-mono text-teal-400">
                    {specialists.length} {isSi ? "වෛද්‍යවරුන්" : "Specialists Available"}
                  </span>
                </label>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {specialists.map((doc) => {
                    const isSelected = selectedDoctor?.doctor_id === doc.doctor_id;
                    return (
                      <div
                        key={doc.doctor_id}
                        onClick={() => handleSelectDoctor(doc)}
                        className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                          isSelected
                            ? "bg-teal-950/60 border-teal-500 ring-1 ring-teal-500/40"
                            : "bg-slate-950 border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="font-bold text-xs text-slate-100">
                              {isSi ? doc.full_name_si : doc.full_name_en}
                            </div>
                            <div className="text-[11px] text-teal-300 font-medium mt-0.5">
                              {isSi ? doc.specialty_si : doc.specialty_en}
                            </div>
                          </div>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-emerald-300 border border-slate-700 shrink-0">
                            LKR {doc.consultation_fee_lkr.toLocaleString()}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-1.5 line-clamp-1">
                          {doc.qualifications}
                        </div>
                        <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                          <span className="truncate">
                            {isSi ? doc.primary_hospital_si : doc.primary_hospital_en}
                          </span>
                          <span className="text-amber-400 shrink-0">★ {doc.rating}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Step 2: Select Channelling Gateway & Consultation Mode */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block">
                    {isSi ? "2. වෙන්කිරීමේ ජාලය (Booking Gateway)" : "2. Sri Lankan Channelling Gateway"}
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { id: "ECHANNELLING", label: "eChannelling (225)" },
                      { id: "DOC990", label: "Doc990 (990)" },
                      { id: "ODOC_TELEMED", label: "oDoc Video" },
                      { id: "HOSPITAL_DIRECT", label: isSi ? "රෝහල හරහා" : "Hospital Direct" }
                    ].map((gw) => (
                      <button
                        type="button"
                        key={gw.id}
                        onClick={() => {
                          setBookingGateway(gw.id);
                          if (gw.id === "ODOC_TELEMED") {
                            setConsultationMode("VIDEO_TELEMEDICINE");
                          }
                        }}
                        className={`px-3 py-2 rounded-lg text-xs font-semibold border text-left transition-all ${
                          bookingGateway === gw.id
                            ? "bg-teal-600 text-white border-teal-400 shadow-sm"
                            : "bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        {gw.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block">
                    {isSi ? "3. හමුවීමේ ක්‍රමය (Consultation Mode)" : "3. Consultation Mode"}
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setConsultationMode("IN_PERSON_HOSPITAL")}
                      className={`px-3 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                        consultationMode === "IN_PERSON_HOSPITAL"
                          ? "bg-teal-600 text-white border-teal-400"
                          : "bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <Building2 className="w-3.5 h-3.5 shrink-0" />
                      <span>{isSi ? "රෝහලට පැමිණ" : "In-Person Hospital"}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setConsultationMode("VIDEO_TELEMEDICINE")}
                      className={`px-3 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                        consultationMode === "VIDEO_TELEMEDICINE"
                          ? "bg-indigo-600 text-white border-indigo-400"
                          : "bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <Video className="w-3.5 h-3.5 shrink-0" />
                      <span>{isSi ? "වීඩියෝ ඇමතුම (Telemed)" : "Video Telemedicine"}</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 3: Select Hospital & Time Slot */}
              {selectedDoctor && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                      {isSi ? "රෝහල තෝරන්න (Select Hospital)" : "Select Hospital Centre"}
                    </label>
                    <select
                      value={selectedHospital}
                      onChange={(e) => setSelectedHospital(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100"
                    >
                      {selectedDoctor.visiting_hospitals.map((h) => (
                        <option key={h} value={h}>
                          {h}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                      {isSi ? "වේලාව තෝරන්න (Available Time Slot)" : "Available Session Time Slot"}
                    </label>
                    <select
                      value={selectedSlot}
                      onChange={(e) => setSelectedSlot(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100"
                    >
                      {selectedDoctor.next_available_slots.map((slot) => (
                        <option key={slot} value={slot}>
                          {slot}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* Step 4: Patient Details & Automated Clinical Handover Preview */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                    {isSi ? "රෝගියාගේ නම (Patient Name)" : "Patient Full Name"}
                  </label>
                  <input
                    type="text"
                    value={patientName}
                    onChange={(e) => setPatientName(e.target.value)}
                    required
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                    {isSi ? "දුරකථන අංකය (Mobile No)" : "Contact Mobile (SMS Token)"}
                  </label>
                  <input
                    type="text"
                    value={patientPhone}
                    onChange={(e) => setPatientPhone(e.target.value)}
                    required
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-slate-400 block mb-1">
                    {isSi ? "වයස (Age)" : "Patient Age"}
                  </label>
                  <input
                    type="number"
                    value={patientAge}
                    onChange={(e) => setPatientAge(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-400 flex items-center justify-between mb-1">
                  <span>
                    {isSi
                      ? "වෛද්‍යවරයා වෙත යොමු කෙරෙන සායනික සාරාංශය (SBAR Handover Summary)"
                      : "Clinical Triage / Lab Findings Summary (Auto-attached to Doctor SBAR Note)"}
                  </span>
                  {icd11Codes.length > 0 && (
                    <span className="font-mono text-[10px] text-teal-400">
                      ICD-11: {icd11Codes.join(", ")}
                    </span>
                  )}
                </label>
                <textarea
                  rows={2}
                  value={clinicalSummary}
                  onChange={(e) => setClinicalSummary(e.target.value)}
                  placeholder={
                    isSi
                      ? "රෝග ලක්ෂණ හෝ රසායනාගාර වාර්තාවේ විස්තර..."
                      : "Symptoms, triage findings, or abnormal lab biomarkers to share with the specialist..."
                  }
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                />
              </div>

              {errorMsg && (
                <div className="p-3 rounded-lg bg-rose-950/70 border border-rose-700 text-rose-200 text-xs">
                  {errorMsg}
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <div className="text-[11px] text-slate-400">
                  {selectedDoctor && (
                    <span>
                      {isSi ? "ඇස්තමේන්තුගත ගාස්තුව:" : "Estimated Channelling Fee:"}{" "}
                      <strong className="text-emerald-400 font-mono">
                        LKR {selectedDoctor.consultation_fee_lkr.toLocaleString()}
                      </strong>
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2.5">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
                  >
                    {isSi ? "අවලංගු කරන්න" : "Cancel"}
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || !selectedDoctor}
                    className="px-5 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 text-white text-xs font-bold shadow-lg transition-all flex items-center gap-1.5 cursor-pointer"
                  >
                    <Calendar className="w-4 h-4" />
                    <span>
                      {submitting
                        ? isSi
                          ? "වෙන්කරමින් පවතී..."
                          : "Confirming Slot..."
                        : isSi
                        ? "වෛද්‍ය හමුව තහවුරු කරන්න (Book Now)"
                        : "Confirm Appointment Booking"}
                    </span>
                  </button>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

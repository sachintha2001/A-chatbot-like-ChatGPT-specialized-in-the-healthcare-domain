"use client";

import React, { useState, useEffect } from "react";
import {
  Stethoscope,
  CalendarCheck,
  Video,
  Building2,
  Search,
  ExternalLink,
  PhoneCall,
  Clock,
  CheckCircle2,
  XCircle,
  FileText,
  Sparkles,
  ShieldCheck
} from "lucide-react";
import {
  SpecialistDoctor,
  PartnerGatewayItem,
  AppointmentBookingResponse
} from "@/lib/types";
import {
  fetchBookingGateways,
  fetchSpecialistDoctors,
  fetchBookedAppointments,
  cancelBookedAppointment
} from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";
import { AppointmentBookingModal } from "@/components/telemedicine/AppointmentBookingModal";

const SPECIALTY_FILTERS = [
  { code: "ALL", labelEn: "All Specialties", labelSi: "සියලුම විශේෂඥ අංශ" },
  { code: "CARDIOLOGY", labelEn: "Cardiologist", labelSi: "හෘද රෝග (Cardiologist)" },
  { code: "HEMATOLOGY", labelEn: "Hematologist", labelSi: "රුධිර රෝග (Hematologist)" },
  { code: "ENDOCRINOLOGY", labelEn: "Endocrinologist", labelSi: "දියවැඩියා / අන්තරාසර්ග" },
  { code: "INFECTIOUS_DISEASE", labelEn: "Physician / Dengue", labelSi: "කායික හා බෝවන රෝග" },
  { code: "PULMONOLOGY", labelEn: "Pulmonologist", labelSi: "ශ්වසන රෝග (Pulmonologist)" },
  { code: "NEUROLOGY", labelEn: "Neurologist", labelSi: "ස්නායු රෝග (Neurologist)" },
  { code: "NEPHROLOGY", labelEn: "Nephrologist", labelSi: "වකුගඩු රෝග (Nephrologist)" },
  { code: "GASTROENTEROLOGY", labelEn: "Gastroenterologist", labelSi: "ආමාශ හා අක්මා රෝග" },
  { code: "GENERAL_MEDICINE", labelEn: "24/7 Tele-GP", labelSi: "වීඩියෝ වෛද්‍ය (oDoc/GP)" }
];

export default function TelemedicineBookingPage() {
  const { language } = useLanguage();
  const isSi = language === "si";

  const [gateways, setGateways] = useState<PartnerGatewayItem[]>([]);
  const [specialists, setSpecialists] = useState<SpecialistDoctor[]>([]);
  const [bookings, setBookings] = useState<AppointmentBookingResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedSpecialty, setSelectedSpecialty] = useState("ALL");
  const [selectedMode, setSelectedMode] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"DIRECTORY" | "BOOKINGS">("DIRECTORY");

  const [modalDoctor, setModalDoctor] = useState<SpecialistDoctor | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [gwRes, docsRes, bookRes] = await Promise.all([
        fetchBookingGateways(),
        fetchSpecialistDoctors({
          specialty: selectedSpecialty,
          mode: selectedMode === "ALL" ? undefined : selectedMode,
          q: searchQuery.trim() || undefined
        }),
        fetchBookedAppointments()
      ]);
      setGateways(gwRes || []);
      setSpecialists(docsRes || []);
      setBookings(bookRes || []);
    } catch {
      // Ignore transient network errors
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSpecialty, selectedMode, searchQuery]);

  const handleOpenBookingForDoctor = (doc: SpecialistDoctor) => {
    setModalDoctor(doc);
    setIsModalOpen(true);
  };

  const handleCancelAppointment = async (bookingId: string) => {
    try {
      await cancelBookedAppointment(bookingId);
      const updated = await fetchBookedAppointments();
      setBookings(updated || []);
    } catch {
      // Ignore
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Hero Banner */}
      <div className="p-6 rounded-2xl bg-slate-950 text-slate-100 border border-slate-800 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-teal-500/15 border border-teal-500/40 flex items-center justify-center text-teal-400 shrink-0">
              <CalendarCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg sm:text-xl font-bold text-white">
                  {isSi
                    ? "සැබෑ විශේෂඥ වෛද්‍යවරුන් හමුවීමේ සහ Telemedicine සේවාව"
                    : "Sri Lankan Specialist Channelling & Telemedicine Hub"}
                </h1>
                <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-teal-950 text-teal-300 border border-teal-700 font-bold">
                  eChannelling • Doc990 • oDoc
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
                {isSi
                  ? "ඔබගේ Triage රෝග ලක්ෂණ හෝ රසායනාගාර වාර්තාවට ගැළපෙන විශේෂඥ වෛද්‍යවරයෙකු (Cardiologist, Hematologist, Endocrinologist, ආදී) eChannelling, Doc990, හෝ oDoc හරහා ස්වයංක්‍රීය SBAR සායනික වාර්තාවක් සමඟ ක්ෂණිකව වෙන්කරවා ගන්න."
                  : "Instantly channel SLMC-registered Specialist Consultants across Asiri, Nawaloka, Lanka Hospitals, Durdans, eChannelling, Doc990, and oDoc 24/7 Video Telemedicine with automated SBAR clinical handover."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("DIRECTORY")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                activeTab === "DIRECTORY"
                  ? "bg-teal-600 text-white shadow-md"
                  : "bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800"
              }`}
            >
              {isSi ? "විශේෂඥ වෛද්‍ය නාමාවලිය" : "Specialist Directory"} ({specialists.length})
            </button>
            <button
              onClick={() => setActiveTab("BOOKINGS")}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                activeTab === "BOOKINGS"
                  ? "bg-teal-600 text-white shadow-md"
                  : "bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800"
              }`}
            >
              <span>{isSi ? "මගේ වෙන්කිරීම් (My Bookings)" : "My Appointments"}</span>
              <span className="px-1.5 py-0.2 rounded-full bg-slate-950 text-teal-300 font-mono text-[10px]">
                {bookings.length}
              </span>
            </button>
          </div>
        </div>

        {/* Partner Gateways Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-5 pt-5 border-t border-slate-800/80">
          {gateways.map((gw) => (
            <a
              key={gw.gateway_id}
              href={gw.portal_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-xl bg-slate-900/90 hover:bg-slate-900 border border-slate-800 hover:border-teal-500/60 transition-all group flex flex-col justify-between"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-100 group-hover:text-teal-300">
                  {isSi ? gw.name_si : gw.name_en}
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400" />
              </div>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                {isSi ? gw.description_si : gw.description_en}
              </p>
              <div className="mt-2 pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] font-mono text-teal-400">
                <span>Hotline: {gw.hotline}</span>
                <span>Connected ✓</span>
              </div>
            </a>
          ))}
        </div>
      </div>

      {activeTab === "DIRECTORY" ? (
        <div className="space-y-5">
          {/* Search & Specialty Filter Bar */}
          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
            <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={
                    isSi
                      ? "වෛද්‍යවරයාගේ නම, රෝහල (Asiri, Nawaloka, Lanka Hospitals) හෝ රෝග ලක්ෂණය සොයන්න..."
                      : "Search by specialist name, hospital (Asiri, Nawaloka, Durdans), or clinical condition (e.g., Dengue, Troponin, Diabetes)..."
                  }
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800 shrink-0">
                {[
                  { id: "ALL", label: isSi ? "සියල්ල" : "All Modes" },
                  { id: "IN_PERSON_HOSPITAL", label: isSi ? "රෝහල් හමුව" : "Hospital Visit" },
                  { id: "VIDEO_TELEMEDICINE", label: isSi ? "වීඩියෝ (Telemed)" : "Video Consult" }
                ].map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setSelectedMode(m.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                      selectedMode === m.id
                        ? "bg-teal-600 text-white"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Specialty Pills */}
            <div className="flex flex-wrap gap-1.5">
              {SPECIALTY_FILTERS.map((sf) => (
                <button
                  key={sf.code}
                  onClick={() => setSelectedSpecialty(sf.code)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all cursor-pointer ${
                    selectedSpecialty === sf.code
                      ? "bg-teal-600 text-white border-teal-400 font-bold shadow-sm"
                      : "bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  {isSi ? sf.labelSi : sf.labelEn}
                </button>
              ))}
            </div>
          </div>

          {/* Specialist Doctor Cards Grid */}
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-500">
              {isSi ? "විශේෂඥ වෛද්‍ය තොරතුරු ලබා ගනිමින් පවතී..." : "Loading Sri Lankan Specialist Directory..."}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {specialists.map((doc) => (
                <div
                  key={doc.doctor_id}
                  className="p-5 rounded-2xl bg-slate-950 border border-slate-800 hover:border-teal-500/60 shadow-lg flex flex-col justify-between space-y-4 transition-all"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="inline-block text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-300 border border-teal-800 font-semibold mb-1.5">
                          {doc.slmc_reg_no} • ★ {doc.rating}
                        </span>
                        <h3 className="text-sm font-bold text-white">
                          {isSi ? doc.full_name_si : doc.full_name_en}
                        </h3>
                        <div className="text-xs font-semibold text-teal-400 mt-0.5">
                          {isSi ? doc.specialty_si : doc.specialty_en}
                        </div>
                      </div>
                      <div className="text-right font-mono shrink-0">
                        <div className="text-[10px] text-slate-400">Fee</div>
                        <div className="text-xs font-bold text-emerald-400">
                          LKR {doc.consultation_fee_lkr.toLocaleString()}
                        </div>
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      {doc.qualifications}
                    </p>

                    <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-xs">
                      <div className="flex items-center gap-2 text-slate-300">
                        <Building2 className="w-3.5 h-3.5 text-teal-400 shrink-0" />
                        <span className="truncate font-medium">
                          {isSi ? doc.primary_hospital_si : doc.primary_hospital_en}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-400 text-[11px]">
                        <Clock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span className="truncate">Next: {doc.next_available_slots[0]}</span>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {doc.supported_gateways.map((gw) => (
                        <span
                          key={gw}
                          className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300"
                        >
                          {gw}
                        </span>
                      ))}
                      {doc.supported_modes.includes("VIDEO_TELEMEDICINE") && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/80 border border-indigo-700 text-indigo-300 flex items-center gap-1">
                          <Video className="w-2.5 h-2.5" />
                          Telemedicine
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleOpenBookingForDoctor(doc)}
                      className="flex-1 py-2.5 px-4 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold shadow-md flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                    >
                      <CalendarCheck className="w-4 h-4" />
                      <span>
                        {isSi ? "වෛද්‍ය හමුවක් වෙන්කරන්න (Book)" : "Book an Appointment"}
                      </span>
                    </button>
                    <a
                      href={doc.echannelling_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      title="Open on eChannelling"
                      className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-teal-300 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* MY CONFIRMED APPOINTMENTS & SBAR HANDOVER SLIPS */
        <div className="space-y-4">
          {bookings.length === 0 ? (
            <div className="p-12 rounded-2xl bg-slate-950 border border-slate-800 text-center space-y-3">
              <CalendarCheck className="w-10 h-10 text-slate-600 mx-auto" />
              <h3 className="text-sm font-bold text-slate-200">
                {isSi ? "දැනට වෙන්කළ වෛද්‍ය හමුවීම් නොමැත" : "No Specialist Appointments Booked Yet"}
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                {isSi
                  ? "විශේෂඥ වෛද්‍ය නාමාවලියෙන් හෝ ඔබගේ රසායනාගාර වාර්තාවේ 'Book Now' බොත්තම මඟින් වෛද්‍ය හමුවක් වෙන්කරවා ගන්න."
                  : "Select a specialist from the directory, Triage Chat, or Lab Report Analyzer to reserve a slot with an automated SBAR handover slip."}
              </p>
              <button
                onClick={() => setActiveTab("DIRECTORY")}
                className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold"
              >
                {isSi ? "වෛද්‍යවරයෙකු තෝරන්න" : "Browse Specialists"}
              </button>
            </div>
          ) : (
            bookings.map((b) => (
              <div
                key={b.booking_id}
                className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4 text-slate-100 shadow-lg"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle2
                      className={`w-6 h-6 shrink-0 mt-0.5 ${
                        b.status === "CONFIRMED" ? "text-emerald-400" : "text-rose-400"
                      }`}
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-teal-300 bg-teal-950 px-2.5 py-0.5 rounded border border-teal-800">
                          {b.booking_reference}
                        </span>
                        <span className="font-mono text-xs font-bold text-amber-300 bg-amber-950/70 px-2 py-0.5 rounded border border-amber-800">
                          Token #{b.queue_token_number}
                        </span>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                            b.status === "CONFIRMED"
                              ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                              : "bg-rose-950 text-rose-300 border border-rose-700"
                          }`}
                        >
                          {b.status}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-white mt-1.5">
                        {isSi ? b.doctor.full_name_si : b.doctor.full_name_en} —{" "}
                        <span className="text-teal-400">
                          {isSi ? b.doctor.specialty_si : b.doctor.specialty_en}
                        </span>
                      </h3>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {b.hospital_or_platform} • {b.scheduled_slot} • Gateway: {b.booking_gateway}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <a
                      href={b.external_gateway_redirect_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold flex items-center gap-1.5"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>{b.booking_gateway}</span>
                    </a>
                    {b.status === "CONFIRMED" && (
                      <button
                        onClick={() => handleCancelAppointment(b.booking_id)}
                        className="px-3 py-1.5 rounded-lg bg-rose-950 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-semibold flex items-center gap-1"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>{isSi ? "අවලංගු කරන්න" : "Cancel"}</span>
                      </button>
                    )}
                  </div>
                </div>

                <pre className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {isSi ? b.sbar_clinical_handover_si : b.sbar_clinical_handover_en}
                </pre>
              </div>
            ))
          )}
        </div>
      )}

      {/* Appointment Booking Modal */}
      <AppointmentBookingModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setModalDoctor(null);
        }}
        preselectedDoctor={modalDoctor}
        onBookingConfirmed={() => {
          fetchBookedAppointments().then((res) => setBookings(res || []));
        }}
      />
    </div>
  );
}

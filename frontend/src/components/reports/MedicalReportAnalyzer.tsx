"use client";

import { useState, useEffect, useRef } from "react";
import {
  UploadCloud,
  FileText,
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowUpRight,
  Sparkles,
  PhoneCall,
  RotateCcw,
  Stethoscope,
  Info,
  Layers,
  ChevronDown,
  ChevronUp,
  Camera,
  CameraOff,
  SwitchCamera,
  Scan,
  Image as ImageIcon,
  Check,
  BookmarkPlus,
  User,
  ExternalLink,
  X,
  CalendarCheck,
  BookOpen,
  Files,
  Download,
  Share2,
  Printer,
  ShieldCheck,
  Award
} from "lucide-react";
import Link from "next/link";
import { ReportAnalysisResult, SampleReportItem, PatientProfileItem } from "@/lib/types";
import {
  uploadMedicalReportFile,
  uploadMedicalReportsBatch,
  analyzeSampleMultipagePdf,
  downloadMedicalAssessmentPdf,
  analyzeReportText,
  fetchSampleReports,
  captureMedicalReportImage,
  fetchPatientProfiles,
  createPatientRecord
} from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";
import { AppointmentBookingModal } from "@/components/telemedicine/AppointmentBookingModal";

export function MedicalReportAnalyzer() {
  const { language } = useLanguage();
  const [inputMode, setInputMode] = useState<"UPLOAD" | "CAMERA" | "TEXT">("UPLOAD");
  const [file, setFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [reportText, setReportText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<ReportAnalysisResult | null>(null);
  const [samples, setSamples] = useState<SampleReportItem[]>([]);
  const [expandedBiomarker, setExpandedBiomarker] = useState<string | null>(null);
  const [showExtractedOcr, setShowExtractedOcr] = useState(false);
  const [selectedPageFilter, setSelectedPageFilter] = useState<number | null>(null);

  // Downloadable Medical Assessment PDF & Official Certificate states
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [pdfPatientName, setPdfPatientName] = useState<string>("Walk-in Patient");
  const [showCertificateModal, setShowCertificateModal] = useState(false);
  const [lastGeneratedRefId, setLastGeneratedRefId] = useState<string | null>(null);

  // Specialist Appointment Booking Modal state
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [bookingSpecialtyHint, setBookingSpecialtyHint] = useState<string>("");

  // Save to EHR profile state
  const [profiles, setProfiles] = useState<PatientProfileItem[]>([]);
  const [selectedProfileToSave, setSelectedProfileToSave] = useState<string>("");
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [savingRecord, setSavingRecord] = useState(false);

  // Camera states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<"environment" | "user">("environment");
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const mobileCaptureRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    fetchSampleReports()
      .then((data) => setSamples(data.samples || []))
      .catch(() => {});
  }, []);

  // Cleanup camera stream when component unmounts or mode changes away from CAMERA
  useEffect(() => {
    if (inputMode === "CAMERA" && !capturedImage) {
      startCameraStream();
    } else {
      stopCameraStream();
    }

    return () => {
      stopCameraStream();
    };
  }, [inputMode, facingMode, capturedImage]);

  const startCameraStream = async () => {
    stopCameraStream();
    setCameraError(null);
    try {
      if (!navigator?.mediaDevices?.getUserMedia) {
        throw new Error(
          language === "si"
            ? "ඔබගේ බ්‍රවුසරය සජීවී කැමරා තාක්ෂණයට සහාය නොදක්වයි. කරුණාකර පහත ගැලරි / ගොනු බොත්තම භාවිත කරන්න."
            : "Live camera access is not supported on this browser. Please use native file upload or mobile photo picker."
        );
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: facingMode },
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      });

      mediaStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(() => {});
      }
      setIsCameraActive(true);
    } catch (err: any) {
      setIsCameraActive(false);
      setCameraError(
        err.name === "NotAllowedError" || err.name === "PermissionDeniedError"
          ? language === "si"
            ? "කැමරාව භාවිතයට බ්‍රවුසර අවසරය ලබා දී නොමැත. කරුණාකර අවසර ලබා දෙන්න හෝ පහත බොත්තමෙන් ඡායාරූපය තෝරන්න."
            : "Camera permission was denied. Please grant permission in browser settings or use the file upload option."
          : err.message || (language === "si" ? "කැමරාව ක්‍රියාත්මක කිරීමට නොහැකි විය." : "Unable to access camera device.")
      );
    }
  };

  const stopCameraStream = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  const switchCamera = () => {
    setFacingMode((prev) => (prev === "environment" ? "user" : "environment"));
  };

  const handleCapturePhoto = () => {
    const video = videoRef.current;
    if (!video) return;

    setIsCapturing(true);

    try {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      const ctx = canvas.getContext("2d");

      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.92);
        setCapturedImage(dataUrl);
        stopCameraStream();
      }
    } catch (err) {
      setErrorMessage(
        language === "si"
          ? "ඡායාරූපය ලබා ගැනීමට නොහැකි විය. කරුණාකර නැවත උත්සාහ කරන්න."
          : "Failed to take snapshot from camera stream."
      );
    } finally {
      setTimeout(() => setIsCapturing(false), 300);
    }
  };

  const handleRetakePhoto = () => {
    setCapturedImage(null);
    setErrorMessage(null);
  };

  const handleMobileCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (uploadEvent) => {
        if (uploadEvent.target?.result) {
          setCapturedImage(uploadEvent.target.result as string);
          stopCameraStream();
        }
      };
      reader.readAsDataURL(selected);
      setErrorMessage(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArr = Array.from(e.target.files);
      setSelectedFiles(filesArr);
      setFile(filesArr[0]);
      setErrorMessage(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArr = Array.from(e.dataTransfer.files);
      setSelectedFiles(filesArr);
      setFile(filesArr[0]);
      setErrorMessage(null);
    }
  };

  const removeSelectedFile = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFiles((prev) => {
      const next = prev.filter((_, idx) => idx !== index);
      setFile(next[0] || null);
      return next;
    });
  };

  const handleAnalyzeSampleMultipagePdf = async () => {
    setLoading(true);
    setErrorMessage(null);
    setSelectedPageFilter(null);
    try {
      const res = await analyzeSampleMultipagePdf({ language });
      if (!res || res.success === false) {
        throw new Error(
          isSi
            ? "බහු-පිටු PDF වාර්තා පොත විශ්ලේෂණය කිරීමට නොහැකි විය."
            : "Failed to analyze the 6-page hospital checkup PDF booklet."
        );
      }
      setAnalysisResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process 6-page sample PDF booklet.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setErrorMessage(null);
    setSelectedPageFilter(null);
    try {
      if (inputMode === "CAMERA") {
        if (!capturedImage) {
          throw new Error(
            isSi
              ? "කරුණාකර කැමරාවෙන් වෛද්‍ය වාර්තාවේ ඡායාරූපයක් ලබා ගන්න."
              : "Please capture a photo of the laboratory report first."
          );
        }
        const res = await captureMedicalReportImage(capturedImage, { language });
        if (!res || res.success === false) {
          throw new Error(
            isSi
              ? (res?.message_si || "වාර්තාවෙන් හඳුනාගත හැකි සායනික පරීක්ෂණ අගයන් සොයාගත නොහැකි විය. කරුණාකර වාර්තාවේ පැහැදිලි ඡායාරූපයක් ලබාගන්න.")
              : (res?.message_en || "No standardized biomarkers could be identified from the photo. Please ensure clear lighting and legible text.")
          );
        }
        setAnalysisResult(res);
      } else if (inputMode === "UPLOAD") {
        const filesToUpload = selectedFiles.length > 0 ? selectedFiles : file ? [file] : [];
        if (filesToUpload.length === 0) {
          throw new Error(
            isSi
              ? "කරුණාකර විශ්ලේෂණය සඳහා වෛද්‍ය වාර්තා ගොනුවක් (Multi-page PDF, පින්තූර, TXT) තෝරන්න."
              : "Please select one or more medical report files (Multi-page PDF, Images, TXT) to upload."
          );
        }
        const res =
          filesToUpload.length > 1
            ? await uploadMedicalReportsBatch(filesToUpload, { language })
            : await uploadMedicalReportFile(filesToUpload[0], { language });
        if (!res || res.success === false) {
          throw new Error(
            isSi
              ? (res?.message_si || "වාර්තාවෙන් හඳුනාගත හැකි සායනික පරීක්ෂණ අගයන් සොයාගත නොහැකි විය. කරුණාකර වාර්තාවේ පැහැදිලි බව පරීක්ෂා කරන්න.")
              : (res?.message_en || "No standardized biomarkers could be identified from the document. Please verify the document content.")
          );
        }
        setAnalysisResult(res);
      } else {
        if (!reportText.trim()) {
          throw new Error(
            isSi
              ? "කරුණාකර රසායනාගාර වාර්තාවේ විස්තර ඇතුළත් කරන්න."
              : "Please paste or type the laboratory report text."
          );
        }
        const res = await analyzeReportText(reportText, { language });
        if (!res || res.success === false) {
          throw new Error(
            isSi
              ? (res?.message_si || "වාර්තාවෙන් හඳුනාගත හැකි සායනික පරීක්ෂණ අගයන් සොයාගත නොහැකි විය. කරුණාකර අගයන් පරීක්ෂා කරන්න.")
              : (res?.message_en || "No standardized biomarkers could be identified from the text. Please check the values.")
          );
        }
        setAnalysisResult(res);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process medical report.");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = (sample: SampleReportItem) => {
    setInputMode("TEXT");
    setReportText(sample.sample_text);
    setErrorMessage(null);
  };

  const resetAnalysis = () => {
    setAnalysisResult(null);
    setFile(null);
    setSelectedFiles([]);
    setReportText("");
    setCapturedImage(null);
    setErrorMessage(null);
    setShowExtractedOcr(false);
    setSelectedPageFilter(null);
  };

  const openSaveModal = async () => {
    try {
      const list = await fetchPatientProfiles();
      setProfiles(list || []);
      if (list && list.length > 0 && !selectedProfileToSave) {
        setSelectedProfileToSave(list[0].id);
      }
      setShowSaveModal(true);
      setSaveSuccess(null);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load patient profiles.");
    }
  };

  const handleSaveToProfile = async () => {
    if (!selectedProfileToSave || !analysisResult) return;
    setSavingRecord(true);
    setErrorMessage(null);
    try {
      const summaryText = isSi
        ? (analysisResult.clinical_directives_si?.join(" ") || analysisResult.overall_status_si)
        : (analysisResult.clinical_directives_en?.join(" ") || analysisResult.overall_status_en);

      await createPatientRecord(selectedProfileToSave, {
        record_type: "LAB_REPORT",
        title: isSi
          ? `රසායනාගාර වාර්තාව (${analysisResult.overall_status_si || analysisResult.overall_status_en})`
          : `Lab Report (${analysisResult.overall_status_en})`,
        overall_status: analysisResult.overall_status,
        qualitative_verdict: analysisResult.qualitative_verdict,
        extracted_biomarkers: analysisResult.parameters || [],
        correlated_icd11: (analysisResult.correlated_conditions || []).map((c) => ({
          icd11: c.icd11,
          condition: c.condition,
          condition_si: c.condition_si,
          urgency: c.urgency
        })),
        notes: summaryText,
        source_filename: analysisResult.filename || "Uploaded Report",
        record_date: new Date().toISOString()
      });

      setSaveSuccess(selectedProfileToSave);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to save record to patient profile.");
    } finally {
      setSavingRecord(false);
    }
  };

  const handleDownloadOfficialPdf = async () => {
    if (!analysisResult) return;
    setDownloadingPdf(true);
    setErrorMessage(null);
    try {
      const { blob, filename, refId } = await downloadMedicalAssessmentPdf(
        analysisResult,
        pdfPatientName.trim() || "Walk-in Patient",
        "Adult / Unspecified"
      );
      setLastGeneratedRefId(refId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate Medical Assessment PDF.");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleShareViaWhatsApp = () => {
    if (!analysisResult) return;
    const refTag = lastGeneratedRefId || analysisResult.batch_job_id || "MGA-PDF-VERIFIED";
    const statusText = isSi
      ? analysisResult.overall_status_si || analysisResult.overall_status_en
      : analysisResult.overall_status_en;
    const elevated = (isSi ? analysisResult.elevated_parameters_si : analysisResult.elevated_parameters_en) || [];
    const decreased = (isSi ? analysisResult.decreased_parameters_si : analysisResult.decreased_parameters_en) || [];
    const icd11Lines = (analysisResult.correlated_conditions || []).map(
      (c) => `• [ICD-11: ${c.icd11}] ${isSi ? c.condition_si : c.condition}`
    );
    const directives = (isSi ? analysisResult.clinical_directives_si : analysisResult.clinical_directives_en) || [];

    const whatsappMessage = [
      `🩺 *MEDGUARD CLINICAL AI — OFFICIAL MEDICAL ASSESSMENT SUMMARY*`,
      `📋 *Ref ID:* ${refTag} | *Patient:* ${pdfPatientName.trim() || "Walk-in Patient"}`,
      `⚖️ *Overall Status:* ${statusText}`,
      analysisResult.qualitative_verdict !== "NOT_APPLICABLE"
        ? `🔬 *Qualitative Verdict:* ${analysisResult.qualitative_verdict}`
        : null,
      ``,
      `📈 *Elevated / High (වැඩි වී ඇති අගයන්):*`,
      elevated.length > 0 ? elevated.map((e) => `  ▲ ${e}`).join("\n") : `  • None (සාමාන්‍යයි)`,
      `📉 *Decreased / Low (අඩු වී ඇති අගයන්):*`,
      decreased.length > 0 ? decreased.map((d) => `  ▼ ${d}`).join("\n") : `  • None (සාමාන්‍යයි)`,
      icd11Lines.length > 0 ? `\n🧬 *WHO ICD-11 Clinical Correlations:*\n${icd11Lines.join("\n")}` : null,
      directives.length > 0
        ? `\n📌 *Clinical Directives (සායනික උපදෙස්):*\n${directives.map((d) => `• ${d}`).join("\n")}`
        : null,
      `\n✅ *Official MedGuard Clinical AI Seal — WHO / IFCC Standardized Handover*`
    ]
      .filter(Boolean)
      .join("\n");

    const waUrl = `https://wa.me/?text=${encodeURIComponent(whatsappMessage)}`;
    window.open(waUrl, "_blank", "noopener,noreferrer");
  };

  const isSi = language === "si";

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 rounded-2xl border border-[#CBE2EA] shadow-clinical-elevated overflow-hidden">
      {/* Top Clinical Diagnostic Header */}
      <div className="clinical-dark-preserve px-6 py-4 bg-gradient-to-r from-[#0A2540] via-[#0E3A5D] to-[#0D7490] border-b border-teal-500/30 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 border border-teal-300/30 flex items-center justify-center text-teal-300 shadow-inner">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-white flex items-center gap-2">
              {isSi ? "සායනික රසායනාගාර වාර්තා විශ්ලේෂණය" : "Clinical Laboratory Report Diagnostic Engine"}
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-teal-400/20 text-teal-200 border border-teal-300/40 font-bold">
                WHO / IFCC Standardized
              </span>
            </h1>
            <p className="text-xs text-cyan-100/80">
              {isSi
                ? "කැමරාවෙන් ඡායාරූපයක් ගෙන හෝ ගොනුවක් උඩුගත කර වාර්තාවේ අගයන් වැඩිද/අඩුද සහ නිල මුද්‍රාව සහිත PDF වාර්තාව ක්ෂණිකව ලබාගන්න"
                : "Multi-Page Batch OCR, WHO Reference Interval Matching, Official Sealed PDF Export & WhatsApp Handover"}
            </p>
          </div>
        </div>

        {analysisResult && (
          <button
            onClick={resetAnalysis}
            className="px-3.5 py-1.5 bg-white/15 hover:bg-white/25 text-white border border-white/20 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{isSi ? "නව වාර්තාවක්" : "New Report"}</span>
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 clinical-ecg-grid">
        {!analysisResult ? (
          /* INPUT & UPLOAD VIEW */
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Input Mode Selector */}
            <div className="flex items-center gap-1.5 p-1.5 bg-slate-900 border border-slate-800 rounded-2xl max-w-xl mx-auto shadow-sm">
              <button
                onClick={() => setInputMode("CAMERA")}
                className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                  inputMode === "CAMERA"
                    ? "bg-gradient-to-r from-teal-600 to-cyan-700 text-white shadow-md font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Camera className={`w-4 h-4 ${inputMode === "CAMERA" ? "text-white" : "text-teal-600"}`} />
                <span>{isSi ? "කැමරාවෙන් ගන්න" : "Live Camera Capture"}</span>
              </button>
              <button
                onClick={() => setInputMode("UPLOAD")}
                className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                  inputMode === "UPLOAD"
                    ? "bg-gradient-to-r from-teal-600 to-cyan-700 text-white shadow-md font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <UploadCloud className="w-4 h-4" />
                <span>{isSi ? "ගොනුවක් උඩුගත කරන්න" : "Upload File (PDF / Image)"}</span>
              </button>
              <button
                onClick={() => setInputMode("TEXT")}
                className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                  inputMode === "TEXT"
                    ? "bg-gradient-to-r from-teal-600 to-cyan-700 text-white shadow-md font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>{isSi ? "අගයන් ටයිප් කරන්න" : "Paste Text"}</span>
              </button>
            </div>

            {/* CAMERA CAPTURE SECTION */}
            {inputMode === "CAMERA" && (
              <div className="space-y-4">
                <input
                  ref={mobileCaptureRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleMobileCapture}
                  className="hidden"
                />

                {!capturedImage ? (
                  /* Live Viewfinder */
                  <div className="camera-viewfinder-dark relative rounded-2xl overflow-hidden border-2 border-teal-500/40 bg-black aspect-[4/3] sm:aspect-[16/10] max-w-xl mx-auto flex flex-col justify-between shadow-lg">
                    {/* Top Status Overlay */}

                    <div className="relative z-10 p-3 bg-gradient-to-b from-black/80 to-transparent flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                        <span className="font-mono text-emerald-400 text-[11px] font-bold">
                          {isSi ? "සජීවී කැමරාව ක්‍රියාත්මකයි" : "LIVE VIEWFINDER"}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={switchCamera}
                          className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-[11px] flex items-center gap-1.5 border border-slate-700 transition-colors"
                        >
                          <SwitchCamera className="w-3.5 h-3.5" />
                          <span>{isSi ? "කැමරාව මාරු කරන්න" : "Flip Camera"}</span>
                        </button>
                      </div>
                    </div>

                    {/* Video Element */}
                    <video
                      ref={videoRef}
                      playsInline
                      muted
                      autoPlay
                      className={`absolute inset-0 w-full h-full object-cover ${
                        isCapturing ? "opacity-30 filter brightness-200 transition-opacity" : "opacity-100"
                      }`}
                    />

                    {/* Viewfinder Target Guidelines */}
                    <div className="absolute inset-0 pointer-events-none flex items-center justify-center p-6">
                      <div className="relative w-full h-full max-w-md max-h-[85%] border-2 border-teal-500/40 rounded-xl flex flex-col items-center justify-between p-3 bg-teal-500/[0.02]">
                        {/* Corner Brackets */}
                        <div className="absolute -top-1 -left-1 w-5 h-5 border-t-2 border-l-2 border-teal-400 rounded-tl" />
                        <div className="absolute -top-1 -right-1 w-5 h-5 border-t-2 border-r-2 border-teal-400 rounded-tr" />
                        <div className="absolute -bottom-1 -left-1 w-5 h-5 border-b-2 border-l-2 border-teal-400 rounded-bl" />
                        <div className="absolute -bottom-1 -right-1 w-5 h-5 border-b-2 border-r-2 border-teal-400 rounded-br" />

                        {/* Animated Laser Scanning Line */}
                        <div className="w-full h-0.5 bg-gradient-to-r from-transparent via-teal-400 to-transparent shadow-[0_0_8px_rgba(45,212,191,0.8)] animate-pulse" />

                        {/* Viewfinder Hint */}
                        <div className="text-center px-3 py-1.5 rounded-lg bg-black/60 backdrop-blur-sm border border-slate-700/60 text-[11px] text-slate-300">
                          <span className="font-semibold text-teal-300">
                            {isSi ? "වෛද්‍ය වාර්තාව රාමුව තුළ කෙලින් තබා ගන්න" : "Align Medical Report Within Guidelines"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Camera Error Alert if stream failed */}
                    {cameraError && (
                      <div className="absolute inset-0 z-20 bg-slate-950/90 flex flex-col items-center justify-center p-6 text-center space-y-3">
                        <CameraOff className="w-10 h-10 text-rose-400" />
                        <p className="text-xs text-rose-300 max-w-sm">{cameraError}</p>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={startCameraStream}
                            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200"
                          >
                            {isSi ? "නැවත උත්සාහ කරන්න" : "Retry Camera"}
                          </button>
                          <button
                            type="button"
                            onClick={() => mobileCaptureRef.current?.click()}
                            className="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-xs font-semibold text-white"
                          >
                            {isSi ? "දුරකථන කැමරාවෙන් තෝරන්න" : "Open Camera / Gallery"}
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Bottom Controls Bar */}
                    <div className="relative z-10 p-4 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() => mobileCaptureRef.current?.click()}
                        className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs flex items-center gap-1.5 transition-colors"
                        title={isSi ? "ගැලරියෙන් හෝ වෙනත් කැමරාවෙන් තෝරන්න" : "Choose from Gallery / Device"}
                      >
                        <ImageIcon className="w-4 h-4 text-teal-400" />
                        <span className="hidden sm:inline">{isSi ? "ගැලරියෙන්" : "Gallery"}</span>
                      </button>

                      {/* Large Shutter Button */}
                      <button
                        type="button"
                        onClick={handleCapturePhoto}
                        disabled={!isCameraActive}
                        className="w-14 h-14 rounded-full border-4 border-white/80 bg-teal-500 hover:bg-teal-400 active:scale-95 disabled:bg-slate-700 disabled:border-slate-600 transition-all shadow-[0_0_20px_rgba(20,184,166,0.5)] flex items-center justify-center cursor-pointer disabled:cursor-not-allowed"
                        aria-label="Capture Report Photo"
                      >
                        <Scan className="w-6 h-6 text-white" />
                      </button>

                      <div className="w-16 text-right">
                        <span className="text-[10px] text-slate-400 font-mono">1080p</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Captured Snapshot Preview */
                  <div className="relative rounded-2xl overflow-hidden border border-teal-500/50 bg-slate-900 max-w-xl mx-auto p-4 space-y-4">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-teal-500/20 text-teal-400 flex items-center justify-center">
                          <Check className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-bold text-slate-200">
                          {isSi ? "ඡායාරූපය සාර්ථකව ලබා ගන්නා ලදී" : "Medical Document Photo Captured"}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={handleRetakePhoto}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1.5 transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>{isSi ? "නැවත ඡායාරූපයක් ගන්න" : "Retake"}</span>
                      </button>
                    </div>

                    <div className="relative rounded-xl overflow-hidden border border-slate-800 max-h-72 flex items-center justify-center bg-black">
                      <img
                        src={capturedImage}
                        alt="Captured Laboratory Report"
                        className="w-full h-full object-contain"
                      />
                      <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-sm px-2 py-0.5 rounded text-[10px] font-mono text-teal-300 border border-teal-800">
                        OCR READY
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 text-center">
                      {isSi
                        ? "අකුරු සහ අගයන් පැහැදිලිදැයි පරීක්ෂා කර පහත 'වාර්තාව සම්පූර්ණයෙන් විශ්ලේෂණය කරන්න' බොත්තම ඔබන්න."
                        : "Ensure the biomarker values and test names are legible, then proceed to analyze."}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* FILE UPLOAD SECTION (Supports Multi-Page PDF Booklets & Batch Image Uploads) */}
            {inputMode === "UPLOAD" && (
              <div className="space-y-3">
                <div
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-slate-800 hover:border-teal-500/60 bg-slate-900/50 hover:bg-slate-900 rounded-2xl p-8 text-center cursor-pointer transition-all space-y-3"
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.txt,.csv,.png,.jpg,.jpeg,.webp"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <div className="w-14 h-14 mx-auto rounded-full bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
                    {selectedFiles.length > 1 ? <Files className="w-7 h-7" /> : <UploadCloud className="w-7 h-7" />}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">
                      {selectedFiles.length > 1
                        ? isSi
                          ? `ගොනු / පිටු ${selectedFiles.length}ක් Batch OCR සඳහා තෝරා ඇත`
                          : `${selectedFiles.length} Report Files / Pages Selected for Batch OCR`
                        : file
                        ? file.name
                        : isSi
                        ? "බහු-පිටු PDF වාර්තා පොතක් (Multi-Page PDF Booklet) හෝ පිටු කිහිපයක් Drag & Drop කරන්න"
                        : "Drag & drop a Multi-Page Hospital PDF Booklet (5–15 pages) or multiple page scans"}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      {selectedFiles.length > 0
                        ? `${(selectedFiles.reduce((acc, f) => acc + f.size, 0) / 1024).toFixed(1)} KB total — Ready for Parallel Asynchronous Batch OCR`
                        : isSi
                        ? "pdf2image + Async Batch OCR මඟින් පිටු 10ක වාර්තාවක් වුවද තත්පර කිහිපයකින් ස්කෑන් කර එකම Dashboard එකකට ගොනු කරයි"
                        : "Powered by pdf2image + Parallel Async Batch OCR — scans 10+ page Health Checkup PDFs in seconds"}
                    </p>
                  </div>

                  {selectedFiles.length > 0 && (
                    <div className="flex flex-wrap items-center justify-center gap-2 pt-1 max-w-xl mx-auto">
                      {selectedFiles.map((f, idx) => (
                        <span
                          key={`${f.name}-${idx}`}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-950 border border-teal-500/40 text-[11px] font-mono text-teal-300"
                        >
                          <FileText className="w-3 h-3 text-teal-400 shrink-0" />
                          <span className="truncate max-w-[180px]">{f.name}</span>
                          <button
                            type="button"
                            onClick={(e) => removeSelectedFile(idx, e)}
                            className="text-slate-400 hover:text-rose-400 ml-0.5"
                            title="Remove file"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
                    <button
                      type="button"
                      className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 inline-flex items-center gap-1.5"
                    >
                      <UploadCloud className="w-3.5 h-3.5 text-teal-400" />
                      <span>
                        {isSi ? "PDF පොතක් හෝ පිටු කිහිපයක් තෝරන්න" : "Browse Multi-Page PDF / Batch Images"}
                      </span>
                    </button>
                  </div>
                </div>

                {/* 1-Click Real 6-Page Hospital PDF Booklet Generator & Async Batch OCR Verification */}
                <div className="p-3.5 rounded-xl bg-gradient-to-r from-teal-950/60 via-slate-900 to-indigo-950/60 border border-teal-500/30 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-teal-500/15 border border-teal-500/40 flex items-center justify-center text-teal-300 shrink-0">
                      <BookOpen className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-100 flex items-center gap-2">
                        <span>
                          {isSi
                            ? "පිටු 6ක සම්පූර්ණ රෝහල් වාර්තා පොතක් (6-Page PDF Booklet) පරීක්ෂා කරන්න"
                            : "Test 6-Page Hospital Comprehensive Checkup PDF Booklet"}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/40">
                          pdf2image + Async Batch OCR
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">
                        {isSi
                          ? "පිටු 6ක සැබෑ PDF වාර්තාවක් (FBC, Lipid, HbA1c, Renal, Liver, Thyroid) තත්පර කිහිපයකින් ස්කෑන් කර එකම Dashboard එකකට ගොනු කරයි."
                          : "Generates & scans a real 6-page PDF booklet (FBC, Lipid, Glycemic, Renal, Liver, Thyroid) into one unified dashboard."}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleAnalyzeSampleMultipagePdf}
                    disabled={loading}
                    className="px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 text-white text-xs font-bold flex items-center gap-1.5 shadow-md transition-all cursor-pointer shrink-0"
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>
                      {isSi ? "පිටු 6ක PDF පොත ස්කෑන් කරන්න" : "Scan 6-Page PDF Booklet Now"}
                    </span>
                  </button>
                </div>
              </div>
            )}

            {/* TEXT INPUT SECTION */}
            {inputMode === "TEXT" && (
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 block">
                  {isSi ? "රසායනාගාර වාර්තාවේ අගයන් ඇතුළත් කරන්න (Paste Report Text):" : "Paste or type clinical laboratory test results:"}
                </label>
                <textarea
                  value={reportText}
                  onChange={(e) => setReportText(e.target.value)}
                  rows={8}
                  placeholder={`Example:\nHemoglobin: 16.5 g/dL\nPlatelet Count: 45000 /uL\nTotal WBC: 3200 /uL\nDengue NS1 Antigen: POSITIVE`}
                  className="w-full bg-slate-900 border border-slate-800 focus:border-teal-500 rounded-xl p-4 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none leading-relaxed"
                />
              </div>
            )}

            {/* Quick Sample Vignettes */}
            <div className="space-y-2 pt-2">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>{isSi ? "ක්ෂණික සායනික නිදසුන් පරීක්ෂා කරන්න (Quick Clinical Presets):" : "Instant Clinical Presets for Real Verification:"}</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {samples.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleLoadSample(s)}
                    className="p-3 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-teal-500 rounded-xl text-left transition-all group"
                  >
                    <div className="font-semibold text-slate-200 group-hover:text-teal-300 flex items-center justify-between">
                      <span>{isSi ? s.title_si : s.title_en}</span>
                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400 shrink-0" />
                    </div>
                    <div className="text-[11px] text-slate-500 font-mono mt-1 truncate">
                      {s.sample_text.split("\n")[1] || s.sample_text.slice(0, 40)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {errorMessage && (
              <div className="p-3.5 bg-rose-950/60 border border-rose-800 text-rose-300 rounded-xl text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Main Submit Action */}
            <div className="text-center pt-2">
              <button
                onClick={handleAnalyze}
                disabled={
                  loading ||
                  (inputMode === "CAMERA" && !capturedImage) ||
                  (inputMode === "UPLOAD" && !file && selectedFiles.length === 0) ||
                  (inputMode === "TEXT" && !reportText.trim())
                }
                className="px-8 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-lg transition-all cursor-pointer disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>
                      {isSi
                        ? "බහු-පිටු සමාන්තර OCR (Async Batch OCR) සහ සායනික දත්ත විශ්ලේෂණය වෙමින් පවතී..."
                        : "Executing Asynchronous Multi-Page Batch OCR & Biomarker Interpretation..."}
                    </span>
                  </>
                ) : (
                  <>
                    <Activity className="w-4 h-4" />
                    <span>{isSi ? "වාර්තාව සම්පූර්ණයෙන් විශ්ලේෂණය කරන්න" : "Execute Full Diagnostic Analysis"}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          /* ANALYSIS REPORT RESULT VIEW */
          (() => {
            const isEmergency = Boolean(analysisResult?.is_emergency);
            const elevatedList = (isSi ? analysisResult?.elevated_parameters_si : analysisResult?.elevated_parameters_en) || [];
            const decreasedList = (isSi ? analysisResult?.decreased_parameters_si : analysisResult?.decreased_parameters_en) || [];
            const correlatedList = analysisResult?.correlated_conditions || [];
            const parametersList = analysisResult?.parameters || [];
            const filteredParametersList =
              selectedPageFilter !== null
                ? parametersList.filter((p) => (p.source_page || 1) === selectedPageFilter)
                : parametersList;
            const pageBreakdownList = analysisResult?.page_breakdown || [];
            const totalPagesScanned = analysisResult?.total_pages_scanned || pageBreakdownList.length || 1;
            const specialistsList = analysisResult?.recommended_specialists || [];
            const directivesList = (isSi ? analysisResult?.clinical_directives_si : analysisResult?.clinical_directives_en) || [];
            const overallStatus = analysisResult?.overall_status || "UNKNOWN";
            const overallStatusText = (isSi ? analysisResult?.overall_status_si : analysisResult?.overall_status_en) || (isSi ? "සායනික තක්සේරු තත්ත්වය" : "Clinical Diagnostic Classification");
            const qualVerdict = analysisResult?.qualitative_verdict || "NOT_APPLICABLE";

            return (
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Overall Status Banner */}
                <div
                  className={`p-5 rounded-2xl border shadow-xl ${
                    isEmergency
                      ? "bg-rose-950/80 border-rose-600 text-rose-100"
                      : overallStatus === "ABNORMAL_ELEVATED_RISK"
                      ? "bg-amber-950/80 border-amber-600 text-amber-100"
                      : "bg-teal-950/80 border-teal-500 text-teal-100"
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      {isEmergency ? (
                        <ShieldAlert className="w-7 h-7 text-rose-400 shrink-0 animate-pulse mt-0.5" />
                      ) : overallStatus === "ABNORMAL_ELEVATED_RISK" ? (
                        <AlertTriangle className="w-7 h-7 text-amber-400 shrink-0 mt-0.5" />
                      ) : (
                        <CheckCircle2 className="w-7 h-7 text-teal-400 shrink-0 mt-0.5" />
                      )}
                      <div>
                        <div className="text-xs font-mono font-bold tracking-wider uppercase opacity-80">
                          {isSi ? "සායනික තක්සේරු තත්ත්වය" : "Overall Diagnostic Classification"}
                        </div>
                        <h2 className="text-base sm:text-lg font-bold mt-1">
                          {overallStatusText}
                        </h2>
                        {qualVerdict !== "NOT_APPLICABLE" && (
                          <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-bold text-xs uppercase bg-teal-950/60 border border-current">
                            <span>
                              {isSi
                                ? `ප්‍රතිඵලය: ${qualVerdict === "POSITIVE" ? "ධනාත්මකයි (POSITIVE)" : "සෘණාත්මකයි (NEGATIVE)"}`
                                : `Qualitative Result: ${qualVerdict}`}
                            </span>
                          </div>
                        )}

                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2.5 shrink-0">
                      {isEmergency && (
                        <a
                          href="tel:1990"
                          className="inline-flex items-center gap-2 px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold shadow-lg transition-colors shrink-0"
                        >
                          <PhoneCall className="w-4 h-4" />
                          <span>{isSi ? "1990 සුවසැරිය / 911 අමතන්න" : "Emergency Direct Dial"}</span>
                        </a>
                      )}
                      <button
                        type="button"
                        onClick={handleDownloadOfficialPdf}
                        disabled={downloadingPdf}
                        className="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-lg transition-colors border border-emerald-400/40 shrink-0 cursor-pointer"
                      >
                        <Download className="w-4 h-4" />
                        <span>
                          {downloadingPdf
                            ? isSi
                              ? "PDF සකසමින්..."
                              : "Generating PDF..."
                            : isSi
                            ? "Download Medical Assessment PDF (නිල වාර්තාව)"
                            : "Download Medical Assessment PDF"}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setBookingSpecialtyHint(specialistsList[0] || "");
                          setIsBookingModalOpen(true);
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg transition-colors border border-indigo-400/30 shrink-0 cursor-pointer"
                      >
                        <CalendarCheck className="w-4 h-4" />
                        <span>
                          {isSi
                            ? "වෛද්‍ය හමුවක් වෙන්කරන්න (eChannelling / Doc990)"
                            : "Book Specialist (eChannelling / Doc990)"}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={openSaveModal}
                        className="inline-flex items-center gap-2 px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold shadow-lg transition-colors border border-teal-400/30 shrink-0"
                      >
                        <BookmarkPlus className="w-4 h-4" />
                        <span>{isSi ? "රෝගී ඉතිහාසයට එක්කරන්න (EHR)" : "Save to Patient EHR"}</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Official Sealed Downloadable Medical Assessment PDF & WhatsApp Doctor Handover Card */}
                <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/60 via-slate-900 to-teal-950/60 border border-emerald-500/40 shadow-lg space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center text-emerald-300 shrink-0">
                        <Award className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-100 flex flex-wrap items-center gap-2">
                          <span>
                            {isSi
                              ? "වෛද්‍යවරයා වෙත ගෙන යාමට හෝ WhatsApp කිරීමට නිල PDF සාරාංශ වාර්තාව"
                              : "Official Sealed Medical Assessment PDF & WhatsApp Physician Handover"}
                          </span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 inline-flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3" />
                            <span>OFFICIAL CLINICAL SEAL</span>
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          {isSi
                            ? "පරීක්ෂා කළ සියලුම අගයන්, වැඩි/අඩු ලක්ෂණ, WHO ICD-11 කේත සහ සායනික උපදෙස් ඇතුළත් නිල මුද්‍රාව සහිත PDF වාර්තාව."
                            : "Includes all tested biomarkers, High/Low flags, WHO ICD-11 codes, clinical directives, and SHA-256 verification seal."}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <input
                        type="text"
                        value={pdfPatientName}
                        onChange={(e) => setPdfPatientName(e.target.value)}
                        placeholder={isSi ? "රෝගියාගේ නම (Patient Name)" : "Patient Name for PDF"}
                        className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-emerald-400 w-44"
                        aria-label="Patient Name for PDF Certificate"
                      />
                      <button
                        type="button"
                        onClick={handleDownloadOfficialPdf}
                        disabled={downloadingPdf}
                        className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white text-xs font-bold inline-flex items-center gap-1.5 shadow-md transition-all cursor-pointer"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>
                          {downloadingPdf
                            ? isSi
                              ? "බාගත වෙමින්..."
                              : "Downloading..."
                            : isSi
                            ? "Download Medical Assessment PDF"
                            : "Download Medical Assessment PDF"}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowCertificateModal(true)}
                        className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer"
                      >
                        <Printer className="w-3.5 h-3.5 text-teal-400" />
                        <span>
                          {isSi ? "නිල මුද්‍රා සහතිකය (සිංහල/EN)" : "Preview Sealed Certificate"}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={handleShareViaWhatsApp}
                        className="px-3 py-2 rounded-xl bg-green-700 hover:bg-green-600 text-white text-xs font-bold inline-flex items-center gap-1.5 shadow-md transition-all cursor-pointer"
                      >
                        <Share2 className="w-3.5 h-3.5" />
                        <span>{isSi ? "WhatsApp (වෛද්‍යවරයාට)" : "WhatsApp to Doctor"}</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Multi-Page PDF & Asynchronous Batch OCR Breakdown Section */}
                {pageBreakdownList.length > 0 && (
                  <div className="p-4 rounded-xl bg-slate-900 border border-teal-500/30 space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <BookOpen className="w-4 h-4 text-teal-400" />
                        <span className="text-xs font-bold text-teal-300 uppercase tracking-wider">
                          {isSi
                            ? `බහු-පිටු වාර්තා පොත් විශ්ලේෂණය (පිටු ${totalPagesScanned}ක් එකම Dashboard එකකට ගොනු කරන ලදී)`
                            : `Multi-Page Booklet Batch OCR (${totalPagesScanned} Pages Consolidated)`}
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
                        {analysisResult?.batch_processing_ms !== undefined && (
                          <span className="px-2 py-0.5 rounded bg-teal-950/80 text-teal-300 border border-teal-800">
                            ⚡ {analysisResult.batch_processing_ms} ms
                          </span>
                        )}
                        {analysisResult?.batch_job_id && (
                          <span className="px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                            Job: {analysisResult.batch_job_id}
                          </span>
                        )}
                        {selectedPageFilter !== null && (
                          <button
                            type="button"
                            onClick={() => setSelectedPageFilter(null)}
                            className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700 hover:bg-indigo-900"
                          >
                            {isSi ? "සියලුම පිටු පෙන්වන්න (Show All Pages)" : "Show All Pages"}
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                      {pageBreakdownList.map((pg) => {
                        const isSelected = selectedPageFilter === pg.page_number;
                        return (
                          <button
                            key={pg.page_number}
                            type="button"
                            onClick={() =>
                              setSelectedPageFilter(isSelected ? null : pg.page_number)
                            }
                            className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                              isSelected
                                ? "bg-teal-950/60 border-teal-400 shadow-md"
                                : "bg-slate-950/80 border-slate-800 hover:border-teal-500/50"
                            }`}
                          >
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">
                                {isSi ? `පිටුව ${pg.page_number}` : `PAGE ${pg.page_number}`}
                              </span>
                              <span
                                className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                                  pg.critical_count > 0
                                    ? "bg-rose-950 text-rose-300 border-rose-700 font-bold"
                                    : pg.abnormal_count > 0
                                    ? "bg-amber-950/80 text-amber-300 border-amber-800"
                                    : "bg-emerald-950/80 text-emerald-300 border-emerald-800"
                                }`}
                              >
                                {pg.abnormal_count > 0
                                  ? isSi
                                    ? `අසාමාන්‍ය ${pg.abnormal_count}`
                                    : `${pg.abnormal_count} Abnormal`
                                  : isSi
                                  ? "සාමාන්‍යයි"
                                  : "Normal"}
                              </span>
                            </div>
                            <div className="text-xs font-bold text-slate-200 mt-1.5 truncate">
                              {isSi ? pg.panel_title_si : pg.panel_title_en}
                            </div>
                            <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono mt-1">
                              <span>
                                {isSi
                                  ? `පරීක්ෂණ ${pg.parameters_detected_count}ක්`
                                  : `${pg.parameters_detected_count} Biomarkers`}
                              </span>
                              <span className="text-slate-500">{pg.extraction_method}</span>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Quick Summary Grid: Elevated (Wedi) vs Decreased (Adu) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Elevated (Wedi) */}
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                        <TrendingUp className="w-4 h-4 text-rose-400" />
                        <span>{isSi ? "වැඩි වී ඇති අගයන් (Elevated / High)" : "Elevated Biomarkers (High)"}</span>
                      </span>
                      <span className="font-mono text-xs font-bold text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800">
                        {analysisResult?.elevated_count ?? elevatedList.length}
                      </span>
                    </div>
                    {elevatedList.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">
                        {isSi ? "සාමාන්‍ය සීමාව ඉක්මවා වැඩි වූ අගයන් නොමැත." : "No biomarkers exceeded the upper reference threshold."}
                      </p>
                    ) : (
                      <ul className="space-y-1 text-xs text-rose-300">
                        {elevatedList.map((item, i) => (
                          <li key={i} className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0" />
                            <span className="font-medium">{item}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  {/* Decreased (Adu) */}
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                        <TrendingDown className="w-4 h-4 text-amber-400" />
                        <span>{isSi ? "අඩු වී ඇති අගයන් (Decreased / Low)" : "Decreased Biomarkers (Low)"}</span>
                      </span>
                      <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800">
                        {analysisResult?.decreased_count ?? decreasedList.length}
                      </span>
                    </div>
                    {decreasedList.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">
                        {isSi ? "සාමාන්‍ය සීමාවට වඩා අඩු වූ අගයන් නොමැත." : "No biomarkers fell below the lower reference threshold."}
                      </p>
                    ) : (
                      <ul className="space-y-1 text-xs text-amber-300">
                        {decreasedList.map((item, i) => (
                          <li key={i} className="flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0" />
                            <span className="font-medium">{item}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                {/* Correlated Clinical Syndromes & ICD-11 */}
                {correlatedList.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                    <div className="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-2">
                      <Layers className="w-4 h-4" />
                      <span>{isSi ? "හඳුනාගත් සායනික රෝග ලක්ෂණ සහ ICD-11 සබඳතා" : "Correlated Clinical Syndromes & ICD-11 Mapping"}</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {correlatedList.map((c, i) => (
                        <div
                          key={i}
                          className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-1 text-xs"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="font-bold text-slate-100">{isSi ? c.condition_si : c.condition}</div>
                            <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800 font-bold shrink-0">
                              ICD-11: {c.icd11}
                            </span>
                          </div>
                          <div className="text-slate-400 text-[11px] leading-relaxed">
                            {isSi ? c.evidence_si : c.evidence}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Detailed Biomarker Breakdown Cards */}
                <div className="space-y-3">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <span>
                      {isSi
                        ? "පරීක්ෂා කළ සියලුම ජෛව රසායනික අගයන් (All Tested Parameters)"
                        : "Tested Clinical Biomarkers Breakdown"}
                      {selectedPageFilter !== null && (
                        <span className="ml-2 text-teal-400">
                          ({isSi ? `පිටුව ${selectedPageFilter} පමණි` : `Filtered: Page ${selectedPageFilter}`})
                        </span>
                      )}
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {filteredParametersList.length} / {analysisResult?.total_parameters_tested ?? parametersList.length} Parameters Evaluated
                    </span>
                  </div>

                  <div className="space-y-2">
                    {filteredParametersList.map((p) => {
                      const isElevated = p.status === "ELEVATED" || p.status === "CRITICAL_HIGH";
                      const isDecreased = p.status === "DECREASED" || p.status === "CRITICAL_LOW";
                      const isPos = p.status === "POSITIVE";
                      const isExpanded = expandedBiomarker === p.canonical_id;

                      const badgeClass = p.is_critical
                        ? "bg-rose-950 text-rose-300 border-rose-700 font-bold"
                        : isElevated
                        ? "bg-rose-950/60 text-rose-300 border-rose-800"
                        : isDecreased
                        ? "bg-amber-950/60 text-amber-300 border-amber-800"
                        : isPos
                        ? "bg-rose-950 text-rose-300 border-rose-700"
                        : "bg-teal-950/60 text-teal-300 border-teal-800";

                      return (
                        <div
                          key={p.canonical_id}
                          className="p-4 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl transition-all"
                        >
                          <div
                            onClick={() => setExpandedBiomarker(isExpanded ? null : p.canonical_id)}
                            className="flex items-center justify-between cursor-pointer"
                          >
                            <div className="flex flex-wrap items-center gap-2.5">
                              {p.source_page && totalPagesScanned > 1 && (
                                <span className="px-1.5 py-0.5 rounded bg-slate-950 text-teal-400 border border-slate-800 text-[10px] font-mono">
                                  {isSi ? `පිටුව ${p.source_page}` : `P.${p.source_page}`}
                                </span>
                              )}
                              <div className="font-semibold text-xs text-slate-200">
                                {isSi ? p.display_name_si : p.display_name_en}
                              </div>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${badgeClass}`}>
                                {isSi ? p.status_si : p.status}
                              </span>
                            </div>

                            <div className="flex items-center gap-4 text-xs">
                              <div className="font-mono text-slate-200 font-bold">
                                {p.raw_value} <span className="text-slate-400 font-normal">{p.unit}</span>
                              </div>
                              {p.ref_interval && (
                                <div className="hidden sm:block text-[11px] font-mono text-slate-500">
                                  Ref: {p.ref_interval} {p.unit}
                                </div>
                              )}
                              {isExpanded ? (
                                <ChevronUp className="w-4 h-4 text-slate-400" />
                              ) : (
                                <ChevronDown className="w-4 h-4 text-slate-400" />
                              )}
                            </div>
                          </div>

                          {isExpanded && (
                            <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs space-y-2 text-slate-400">
                              <div>
                                <span className="font-semibold text-slate-300">
                                  {isSi ? "සායනික අර්ථකථනය:" : "Clinical Interpretation:"}{" "}
                                </span>
                                {isSi ? p.interpretation_si : p.interpretation_en}
                              </div>
                              {p.related_icd11 && p.related_icd11.length > 0 && (
                                <div className="flex items-center gap-2 pt-1">
                                  <span className="text-[11px] font-semibold text-slate-400">WHO ICD-11:</span>
                                  <div className="flex gap-1">
                                    {p.related_icd11.map((code) => (
                                      <span
                                        key={code}
                                        className="px-1.5 py-0.2 rounded bg-slate-800 text-teal-400 font-mono text-[10px]"
                                      >
                                        {code}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* OCR Extracted Text Preview Toggle */}
                {analysisResult?.extracted_text_preview && (
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <button
                      type="button"
                      onClick={() => setShowExtractedOcr(!showExtractedOcr)}
                      className="w-full flex items-center justify-between text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
                    >
                      <span className="flex items-center gap-1.5">
                        <Scan className="w-3.5 h-3.5 text-teal-400" />
                        <span>{isSi ? "හඳුනාගත් OCR අක්ෂර පෙළ (Extracted Raw Text)" : "Extracted OCR Document Transcript"}</span>
                      </span>
                      {showExtractedOcr ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>

                    {showExtractedOcr && (
                      <pre className="p-3 bg-slate-950 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap leading-relaxed border border-slate-800">
                        {analysisResult.extracted_text_preview}
                      </pre>
                    )}
                  </div>
                )}

                {/* Recommended Specialists & Instant Booking */}
                {specialistsList.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3 text-xs">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                        <Stethoscope className="w-4 h-4 text-teal-400" />
                        <span>
                          {isSi
                            ? "නිර්දේශිත විශේෂඥ වෛද්‍ය අංශ සහ ක්ෂණික වෙන්කිරීම (eChannelling / Doc990)"
                            : "Recommended Specialist Referrals & Instant Channelling"}
                        </span>
                      </div>
                      <Link
                        href="/telemedicine"
                        className="text-[11px] font-semibold text-teal-400 hover:text-teal-300 flex items-center gap-1"
                      >
                        <span>{isSi ? "සියලුම වෛද්‍යවරුන් බලන්න" : "View Full Specialist Directory"}</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                      {specialistsList.map((spec, i) => (
                        <div
                          key={i}
                          className="p-3 rounded-xl bg-slate-950 border border-slate-800 hover:border-teal-500/60 flex items-center justify-between gap-3 transition-all"
                        >
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 shrink-0">
                              <Stethoscope className="w-4 h-4" />
                            </div>
                            <div>
                              <div className="font-bold text-slate-200 text-xs">{spec}</div>
                              <div className="text-[10px] text-slate-400">
                                {isSi
                                  ? "eChannelling • Doc990 • oDoc Video"
                                  : "Available on eChannelling, Doc990 & oDoc"}
                              </div>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              setBookingSpecialtyHint(spec);
                              setIsBookingModalOpen(true);
                            }}
                            className="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-bold flex items-center gap-1.5 shrink-0 shadow-sm transition-colors cursor-pointer"
                          >
                            <CalendarCheck className="w-3.5 h-3.5" />
                            <span>{isSi ? "වෙන්කරන්න (Book)" : "Book Now"}</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Clinical Directives & Next Steps */}
                {directivesList.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
                    <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                      <Info className="w-4 h-4 text-teal-400" />
                      <span>{isSi ? "ක්ෂණික සායනික උපදෙස් සහ ආරක්ෂණ ක්‍රියාමාර්ග" : "Clinical Action Directives & Safety Netting"}</span>
                    </div>
                    <ul className="space-y-1.5 text-slate-300 pt-1">
                      {directivesList.map((dir, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-teal-400 font-bold">•</span>
                          <span className="leading-relaxed">{dir}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })()
        )}
      </div>

      {/* Save to Patient Profile (EHR) Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              onClick={() => {
                setShowSaveModal(false);
                setSaveSuccess(null);
              }}
              className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
                <BookmarkPlus className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100">
                  {isSi ? "රෝගී ඉතිහාසයට ඇතුළත් කරන්න (EHR)" : "Save to Patient Health Record (EHR)"}
                </h3>
                <p className="text-xs text-slate-400">
                  {isSi
                    ? "මෙම රසායනාගාර වාර්තාවේ අගයන් පවුලේ සාමාජිකයෙකුගේ පැතිකඩට එක්කර ප්‍රවණතා විශ්ලේෂණය කරන්න"
                    : "Attach this lab report to a patient profile to track longitudinal biomarker trajectories"}
                </p>
              </div>
            </div>

            {saveSuccess ? (
              <div className="space-y-4 py-2">
                <div className="p-4 rounded-xl bg-teal-950/60 border border-teal-600/50 flex items-center gap-3 text-teal-300 text-xs">
                  <Check className="w-5 h-5 text-teal-400 shrink-0" />
                  <div>
                    <div className="font-bold">
                      {isSi ? "වාර්තාව සාර්ථකව රෝගී පැතිකඩට එක්කරන ලදී!" : "Report successfully saved to patient profile!"}
                    </div>
                    <div className="text-[11px] text-teal-400/80 mt-0.5">
                      {isSi
                        ? "ජෛව සලකුණු ප්‍රවණතා සහ කාලානුක්‍රමික සටහන් යාවත්කාලීන විය."
                        : "Biomarker trends and longitudinal trajectory charts have been updated."}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    onClick={() => {
                      setShowSaveModal(false);
                      setSaveSuccess(null);
                    }}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
                  >
                    {isSi ? "වසන්න" : "Close"}
                  </button>
                  <Link
                    href={`/records?profile=${saveSuccess}`}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition-colors"
                  >
                    <span>{isSi ? "රෝගී ඉතිහාසය සහ ප්‍රස්ථාර බලන්න" : "View Patient EHR & Trends"}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-2">
                    {isSi ? "රෝගී පැතිකඩ තෝරන්න (Select Profile)" : "Select Patient Profile"}
                  </label>
                  {profiles.length === 0 ? (
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-400">
                      {isSi ? "රෝගී පැතිකඩ හමු නොවීය. කරුණාකර පළමුව පැතිකඩක් සාදන්න." : "No patient profiles found. Please create one in Records."}
                    </div>
                  ) : (
                    <select
                      value={selectedProfileToSave}
                      onChange={(e) => setSelectedProfileToSave(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                    >
                      {profiles.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.full_name} ({p.relationship}) - {p.biological_sex}, {p.blood_group || "Unknown Blood Group"}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                {/* Report Summary Card in Modal */}
                <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 space-y-1.5 text-xs text-slate-300">
                  <div className="font-semibold text-slate-200">
                    {isSi ? "වාර්තා සාරාංශය (To be saved):" : "Record Summary to be saved:"}
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{isSi ? "හඳුනාගත් ජෛව සලකුණු:" : "Biomarkers parsed:"}</span>
                    <span className="font-mono text-teal-400 font-bold">{analysisResult?.parameters?.length || 0}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{isSi ? "තත්ත්වය:" : "Diagnostic classification:"}</span>
                    <span className="font-bold text-slate-200">{analysisResult?.overall_status_en}</span>
                  </div>
                  {(analysisResult?.abnormal_count || 0) > 0 && (
                    <div className="flex items-center justify-between text-[11px] text-rose-400">
                      <span>{isSi ? "අසාමාන්‍ය අගයන්:" : "Abnormal flags:"}</span>
                      <span className="font-mono font-bold">{analysisResult?.abnormal_count}</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowSaveModal(false)}
                    disabled={savingRecord}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors"
                  >
                    {isSi ? "අවලංගු කරන්න" : "Cancel"}
                  </button>
                  <button
                    type="button"
                    onClick={handleSaveToProfile}
                    disabled={savingRecord || profiles.length === 0}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-xl text-xs font-bold transition-colors shadow-lg"
                  >
                    {savingRecord ? (
                      <span>{isSi ? "සුරකිමින් පවතී..." : "Saving..."}</span>
                    ) : (
                      <>
                        <BookmarkPlus className="w-3.5 h-3.5" />
                        <span>{isSi ? "සුරකින්න (Confirm & Save)" : "Confirm & Save"}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Official Sealed Medical Assessment Certificate Modal (Bilingual Sinhala + English Print / PDF / WhatsApp) */}
      {showCertificateModal && analysisResult && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-2xl max-w-4xl w-full max-h-[92vh] overflow-y-auto p-6 space-y-5 shadow-2xl relative">
            {/* Top Action Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <Award className="w-5 h-5 text-emerald-400" />
                <span className="text-sm font-bold text-slate-100">
                  {isSi
                    ? "නිල මුද්‍රාව සහිත වෛද්‍ය තක්සේරු සාරාංශ වාර්තාව (Official Clinical Handover Certificate)"
                    : "Official Sealed Medical Assessment Summary Certificate"}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={handleDownloadOfficialPdf}
                  disabled={downloadingPdf}
                  className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold inline-flex items-center gap-1.5 shadow-md cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>{isSi ? "Download Official PDF (.pdf)" : "Download Official PDF (.pdf)"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold inline-flex items-center gap-1.5 cursor-pointer"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>{isSi ? "මුද්‍රණය කරන්න (Print)" : "Print Certificate"}</span>
                </button>
                <button
                  type="button"
                  onClick={handleShareViaWhatsApp}
                  className="px-3 py-1.5 rounded-xl bg-green-700 hover:bg-green-600 text-white text-xs font-bold inline-flex items-center gap-1.5 cursor-pointer"
                >
                  <Share2 className="w-3.5 h-3.5" />
                  <span>WhatsApp</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowCertificateModal(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Printable Certificate Paper Sheet */}
            <div className="bg-slate-950 border-2 border-emerald-500/30 rounded-2xl p-6 space-y-5 text-xs">
              {/* Official Letterhead */}
              <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="text-[11px] font-mono text-emerald-400 font-bold tracking-wider uppercase">
                    MEDGUARD CLINICAL AI — WHO / IFCC STANDARDIZED DIAGNOSTIC HANDOVER
                  </div>
                  <h2 className="text-base sm:text-lg font-bold text-slate-100 mt-1">
                    {isSi
                      ? "සායනික රසායනාගාර පරීක්ෂණ නිල සාරාංශ වාර්තාව"
                      : "Official Clinical Laboratory Assessment & Physician Handover Report"}
                  </h2>
                  <div className="text-[11px] text-slate-400 font-mono mt-1">
                    Ref ID: {lastGeneratedRefId || analysisResult.batch_job_id || "MGA-PDF-VERIFIED"} • Patient:{" "}
                    <span className="text-slate-200 font-bold">{pdfPatientName || "Walk-in Patient"}</span> • Pages
                    Evaluated: {analysisResult.total_pages_scanned || 1}
                  </div>
                </div>

                {/* Official Circular Seal Stamp */}
                <div className="px-4 py-2.5 rounded-2xl border-2 border-double border-emerald-400/70 bg-emerald-950/40 text-center shrink-0">
                  <div className="flex items-center justify-center gap-1 text-emerald-300 font-mono text-[10px] font-bold uppercase tracking-widest">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>OFFICIAL CLINICAL SEAL</span>
                  </div>
                  <div className="text-[11px] font-bold text-slate-100 mt-0.5">
                    {isSi ? "නිල සායනික තක්සේරු මුද්‍රාව" : "VERIFIED DIAGNOSTIC HANDOVER"}
                  </div>
                  <div className="text-[9px] font-mono text-emerald-400/90">
                    WHO ICD-11 & IFCC COMPLIANT
                  </div>
                </div>
              </div>

              {/* Overall Verdict Box */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-[10px] font-mono uppercase text-slate-400">
                    {isSi ? "සමස්ත සායනික තීරණය / Overall Classification" : "Overall Clinical Classification"}
                  </div>
                  <div className="text-sm font-bold text-slate-100 mt-0.5">
                    {analysisResult.overall_status_si} / {analysisResult.overall_status_en}
                  </div>
                </div>
                {analysisResult.qualitative_verdict !== "NOT_APPLICABLE" && (
                  <span className="px-3 py-1 rounded-full bg-teal-950 text-teal-300 border border-teal-700 font-mono text-xs font-bold">
                    Verdict: {analysisResult.qualitative_verdict}
                  </span>
                )}
              </div>

              {/* Elevated vs Decreased Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-rose-950/30 border border-rose-800/60 space-y-1">
                  <div className="font-bold text-rose-300">
                    ▲ {isSi ? "වැඩි වී ඇති අගයන් (Elevated / High)" : "Elevated / High Biomarkers"} (
                    {analysisResult.elevated_count})
                  </div>
                  <div className="text-slate-300 text-[11px]">
                    {(isSi ? analysisResult.elevated_parameters_si : analysisResult.elevated_parameters_en)?.join(
                      ", "
                    ) || (isSi ? "සාමාන්‍ය සීමාව ඉක්මවා නැත" : "None")}
                  </div>
                </div>
                <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-800/60 space-y-1">
                  <div className="font-bold text-amber-300">
                    ▼ {isSi ? "අඩු වී ඇති අගයන් (Decreased / Low)" : "Decreased / Low Biomarkers"} (
                    {analysisResult.decreased_count})
                  </div>
                  <div className="text-slate-300 text-[11px]">
                    {(isSi ? analysisResult.decreased_parameters_si : analysisResult.decreased_parameters_en)?.join(
                      ", "
                    ) || (isSi ? "සාමාන්‍ය සීමාවට වඩා අඩු වී නැත" : "None")}
                  </div>
                </div>
              </div>

              {/* Tested Biomarkers Table */}
              <div className="space-y-2">
                <div className="font-bold text-slate-300 uppercase tracking-wider text-[11px]">
                  {isSi
                    ? `පරීක්ෂා කළ සියලුම ජෛව රසායනික අගයන් (${analysisResult.parameters?.length || 0})`
                    : `Complete Tested Biomarkers Table (${analysisResult.parameters?.length || 0})`}
                </div>
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left border-collapse text-[11px]">
                    <thead>
                      <tr className="bg-slate-900 text-slate-400 font-mono border-b border-slate-800">
                        <th className="p-2.5">Parameter (පරීක්ෂණය)</th>
                        <th className="p-2.5">Result (අගය)</th>
                        <th className="p-2.5">Ref. Interval (සාමාන්‍ය පරාසය)</th>
                        <th className="p-2.5">Status (තත්ත්වය)</th>
                        <th className="p-2.5">Page</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {(analysisResult.parameters || []).map((p) => (
                        <tr key={p.canonical_id} className="bg-slate-950/60">
                          <td className="p-2.5 font-semibold text-slate-200">
                            <div>{p.display_name_en}</div>
                            <div className="text-[10px] text-slate-400">{p.display_name_si}</div>
                          </td>
                          <td className="p-2.5 font-mono font-bold text-slate-100">
                            {p.raw_value} {p.unit}
                          </td>
                          <td className="p-2.5 font-mono text-slate-400">
                            {p.ref_interval ? `${p.ref_interval} ${p.unit}` : "Qualitative"}
                          </td>
                          <td className="p-2.5 font-mono">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] border ${
                                p.is_critical
                                  ? "bg-rose-950 text-rose-300 border-rose-700 font-bold"
                                  : p.is_abnormal
                                  ? "bg-amber-950 text-amber-300 border-amber-700"
                                  : "bg-teal-950 text-teal-300 border-teal-800"
                              }`}
                            >
                              {p.status} / {p.status_si}
                            </span>
                          </td>
                          <td className="p-2.5 font-mono text-slate-400">P.{p.source_page || 1}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Correlated ICD-11 Codes */}
              {(analysisResult.correlated_conditions || []).length > 0 && (
                <div className="space-y-1.5">
                  <div className="font-bold text-teal-400 uppercase tracking-wider text-[11px]">
                    WHO ICD-11 Clinical Correlations (හඳුනාගත් රෝග ලක්ෂණ සහ ICD-11 කේත)
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {analysisResult.correlated_conditions.map((c, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                        <div className="flex items-center justify-between font-bold text-slate-200">
                          <span>
                            {c.condition_si} ({c.condition})
                          </span>
                          <span className="font-mono text-teal-400 text-[10px]">ICD-11: {c.icd11}</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">{c.evidence_si || c.evidence}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Clinical Directives */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
                <div className="font-bold text-slate-200">
                  {isSi
                    ? "සායනික උපදෙස් සහ නිර්දේශිත විශේෂඥ වෛද්‍ය අංශ (Clinical Directives & Referrals)"
                    : "Clinical Directives & Specialist Referrals"}
                </div>
                <div className="text-[11px] text-teal-300 font-semibold">
                  {(analysisResult.recommended_specialists || []).join(" • ")}
                </div>
                <ul className="space-y-1 text-slate-300 text-[11px] pt-1">
                  {((isSi ? analysisResult.clinical_directives_si : analysisResult.clinical_directives_en) || []).map(
                    (d, i) => (
                      <li key={i}>• {d}</li>
                    )
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Specialist Appointment Booking Modal (eChannelling / Doc990 / oDoc) */}
      <AppointmentBookingModal
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        specialtyHint={bookingSpecialtyHint || analysisResult?.recommended_specialists?.[0]}
        clinicalContext={
          analysisResult
            ? `${analysisResult.overall_status_en}. Elevated: ${(analysisResult.elevated_parameters_en || []).join(", ") || "None"}. Decreased: ${(analysisResult.decreased_parameters_en || []).join(", ") || "None"}.`
            : ""
        }
        triageAcuity={
          analysisResult?.is_emergency
            ? "EMERGENCY"
            : analysisResult?.overall_status === "ABNORMAL_ELEVATED_RISK"
            ? "URGENT"
            : "ROUTINE"
        }
        icd11Codes={(analysisResult?.correlated_conditions || []).map((c) => c.icd11)}
      />
    </div>
  );
}

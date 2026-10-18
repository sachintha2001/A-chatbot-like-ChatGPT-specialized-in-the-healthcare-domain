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
  Check
} from "lucide-react";
import { ReportAnalysisResult, SampleReportItem } from "@/lib/types";
import {
  uploadMedicalReportFile,
  analyzeReportText,
  fetchSampleReports,
  captureMedicalReportImage
} from "@/lib/api";
import { useLanguage } from "@/lib/LanguageContext";

export function MedicalReportAnalyzer() {
  const { language } = useLanguage();
  const [inputMode, setInputMode] = useState<"UPLOAD" | "CAMERA" | "TEXT">("UPLOAD");
  const [file, setFile] = useState<File | null>(null);
  const [reportText, setReportText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<ReportAnalysisResult | null>(null);
  const [samples, setSamples] = useState<SampleReportItem[]>([]);
  const [expandedBiomarker, setExpandedBiomarker] = useState<string | null>(null);
  const [showExtractedOcr, setShowExtractedOcr] = useState(false);

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
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMessage(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setErrorMessage(null);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      if (inputMode === "CAMERA") {
        if (!capturedImage) {
          throw new Error(
            language === "si"
              ? "කරුණාකර කැමරාවෙන් වෛද්‍ය වාර්තාවේ ඡායාරූපයක් ලබා ගන්න."
              : "Please capture a photo of the laboratory report first."
          );
        }
        const res = await captureMedicalReportImage(capturedImage, { language });
        setAnalysisResult(res);
      } else if (inputMode === "UPLOAD") {
        if (!file) {
          throw new Error(
            language === "si"
              ? "කරුණාකර විශ්ලේෂණය සඳහා වෛද්‍ය වාර්තා ගොනුවක් (PDF, පින්තූරයක්, TXT) තෝරන්න."
              : "Please select a medical report file (PDF, Image, TXT) to upload."
          );
        }
        const res = await uploadMedicalReportFile(file, { language });
        setAnalysisResult(res);
      } else {
        if (!reportText.trim()) {
          throw new Error(
            language === "si"
              ? "කරුණාකර රසායනාගාර වාර්තාවේ විස්තර ඇතුළත් කරන්න."
              : "Please paste or type the laboratory report text."
          );
        }
        const res = await analyzeReportText(reportText, { language });
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
    setReportText("");
    setCapturedImage(null);
    setErrorMessage(null);
    setShowExtractedOcr(false);
  };

  const isSi = language === "si";

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 rounded-xl border border-slate-800 shadow-2xl overflow-hidden">
      {/* Top Header */}
      <div className="px-6 py-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-slate-100 flex items-center gap-2">
              {isSi ? "සායනික රසායනාගාර වාර්තා විශ්ලේෂණය" : "Clinical Laboratory Report Diagnostic Engine"}
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800 font-bold">
                WHO / IFCC Standardized
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              {isSi
                ? "කැමරාවෙන් ඡායාරූපයක් ගෙන හෝ ගොනුවක් උඩුගත කර වාර්තාවේ අගයන් වැඩිද/අඩුද සහ ධනාත්මක/සෘණාත්මක බව ක්ෂණිකව පරික්ෂා කරන්න"
                : "Automated OCR Parsing, Reference Interval Matching, and Clinical Positive/Negative Triaging"}
            </p>
          </div>
        </div>

        {analysisResult && (
          <button
            onClick={resetAnalysis}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{isSi ? "නව වාර්තාවක්" : "New Report"}</span>
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {!analysisResult ? (
          /* INPUT & UPLOAD VIEW */
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Input Mode Selector */}
            <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl max-w-lg mx-auto">
              <button
                onClick={() => setInputMode("CAMERA")}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                  inputMode === "CAMERA"
                    ? "bg-teal-600 text-white shadow-md font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Camera className="w-4 h-4 text-teal-300" />
                <span>{isSi ? "කැමරාවෙන් ගන්න" : "Live Camera Capture"}</span>
              </button>
              <button
                onClick={() => setInputMode("UPLOAD")}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                  inputMode === "UPLOAD"
                    ? "bg-teal-600 text-white shadow-md font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <UploadCloud className="w-4 h-4" />
                <span>{isSi ? "ගොනුවක් උඩුගත කරන්න" : "Upload File (PDF / Image)"}</span>
              </button>
              <button
                onClick={() => setInputMode("TEXT")}
                className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                  inputMode === "TEXT"
                    ? "bg-teal-600 text-white shadow-md font-bold"
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
                  <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-black aspect-[4/3] sm:aspect-[16/10] max-w-xl mx-auto flex flex-col justify-between">
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

            {/* FILE UPLOAD SECTION */}
            {inputMode === "UPLOAD" && (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-800 hover:border-teal-500/60 bg-slate-900/50 hover:bg-slate-900 rounded-2xl p-10 text-center cursor-pointer transition-all space-y-3"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.csv,.png,.jpg,.jpeg,.webp"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <div className="w-14 h-14 mx-auto rounded-full bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
                  <UploadCloud className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-100">
                    {file
                      ? file.name
                      : isSi
                      ? "ඔබගේ වෛද්‍ය වාර්තාව මෙතැනට Drag & Drop කරන්න"
                      : "Drag and drop your laboratory report here"}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    {file
                      ? `${(file.size / 1024).toFixed(1)} KB - Ready for diagnostic parsing`
                      : isSi
                      ? "PDF, ඡායාරූප (PNG/JPG), TXT, හෝ CSV ගොනු සහාය දක්වයි"
                      : "Supports PDF, Scans/Photos (PNG, JPG, WEBP), or TXT documents"}
                  </p>
                </div>
                <button
                  type="button"
                  className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 inline-block"
                >
                  {isSi ? "ගොනුව තෝරන්න" : "Browse Files"}
                </button>
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
                  (inputMode === "UPLOAD" && !file) ||
                  (inputMode === "TEXT" && !reportText.trim())
                }
                className="px-8 py-3 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-lg transition-all cursor-pointer disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>
                      {isSi
                        ? "ප්‍රකාශ අක්ෂර හඳුනාගැනීම (OCR) සහ සායනික දත්ත විශ්ලේෂණය වෙමින් පවතී..."
                        : "Executing High-Precision OCR & Clinical Biomarker Interpretation..."}
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
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Overall Status Banner */}
            <div
              className={`p-5 rounded-2xl border shadow-xl ${
                analysisResult.is_emergency
                  ? "bg-rose-950/80 border-rose-600 text-rose-100"
                  : analysisResult.overall_status === "ABNORMAL_ELEVATED_RISK"
                  ? "bg-amber-950/80 border-amber-600 text-amber-100"
                  : "bg-teal-950/80 border-teal-500 text-teal-100"
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  {analysisResult.is_emergency ? (
                    <ShieldAlert className="w-7 h-7 text-rose-400 shrink-0 animate-pulse mt-0.5" />
                  ) : analysisResult.overall_status === "ABNORMAL_ELEVATED_RISK" ? (
                    <AlertTriangle className="w-7 h-7 text-amber-400 shrink-0 mt-0.5" />
                  ) : (
                    <CheckCircle2 className="w-7 h-7 text-teal-400 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <div className="text-xs font-mono font-bold tracking-wider uppercase opacity-80">
                      {isSi ? "සායනික තක්සේරු තත්ත්වය" : "Overall Diagnostic Classification"}
                    </div>
                    <h2 className="text-base sm:text-lg font-bold mt-1">
                      {isSi ? analysisResult.overall_status_si : analysisResult.overall_status_en}
                    </h2>
                    {analysisResult.qualitative_verdict !== "NOT_APPLICABLE" && (
                      <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-bold text-xs uppercase bg-black/40 border border-current">
                        <span>
                          {isSi
                            ? `ප්‍රතිඵලය: ${analysisResult.qualitative_verdict === "POSITIVE" ? "ධනාත්මකයි (POSITIVE)" : "සෘණාත්මකයි (NEGATIVE)"}`
                            : `Qualitative Result: ${analysisResult.qualitative_verdict}`}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {analysisResult.is_emergency && (
                  <a
                    href="tel:1990"
                    className="inline-flex items-center gap-2 px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold shadow-lg transition-colors shrink-0"
                  >
                    <PhoneCall className="w-4 h-4" />
                    <span>{isSi ? "1990 සුවසැරිය / 911 අමතන්න" : "Emergency Direct Dial"}</span>
                  </a>
                )}
              </div>
            </div>

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
                    {analysisResult.elevated_count}
                  </span>
                </div>
                {analysisResult.elevated_count === 0 ? (
                  <p className="text-xs text-slate-500 italic">
                    {isSi ? "සාමාන්‍ය සීමාව ඉක්මවා වැඩි වූ අගයන් නොමැත." : "No biomarkers exceeded the upper reference threshold."}
                  </p>
                ) : (
                  <ul className="space-y-1 text-xs text-rose-300">
                    {(isSi ? analysisResult.elevated_parameters_si : analysisResult.elevated_parameters_en).map((item, i) => (
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
                    {analysisResult.decreased_count}
                  </span>
                </div>
                {analysisResult.decreased_count === 0 ? (
                  <p className="text-xs text-slate-500 italic">
                    {isSi ? "සාමාන්‍ය සීමාවට වඩා අඩු වූ අගයන් නොමැත." : "No biomarkers fell below the lower reference threshold."}
                  </p>
                ) : (
                  <ul className="space-y-1 text-xs text-amber-300">
                    {(isSi ? analysisResult.decreased_parameters_si : analysisResult.decreased_parameters_en).map((item, i) => (
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
            {analysisResult.correlated_conditions.length > 0 && (
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="text-xs font-bold text-teal-400 uppercase tracking-wider flex items-center gap-2">
                  <Layers className="w-4 h-4" />
                  <span>{isSi ? "හඳුනාගත් සායනික රෝග ලක්ෂණ සහ ICD-11 සබඳතා" : "Correlated Clinical Syndromes & ICD-11 Mapping"}</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {analysisResult.correlated_conditions.map((c, i) => (
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
                <span>{isSi ? "පරීක්ෂා කළ සියලුම ජෛව රසායනික අගයන් (All Tested Parameters)" : "Tested Clinical Biomarkers Breakdown"}</span>
                <span className="text-[11px] text-slate-500 font-mono">
                  {analysisResult.total_parameters_tested} Parameters Evaluated
                </span>
              </div>

              <div className="space-y-2">
                {analysisResult.parameters.map((p) => {
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
                        <div className="flex items-center gap-3">
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
            {analysisResult.extracted_text_preview && (
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

            {/* Recommended Specialists */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Stethoscope className="w-4 h-4 text-teal-400" />
                <span>{isSi ? "නිර්දේශිත විශේෂඥ වෛද්‍ය අංශ (Recommended Specialists)" : "Recommended Specialist Referrals"}</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {analysisResult.recommended_specialists.map((spec, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-300 text-xs font-medium"
                  >
                    {spec}
                  </span>
                ))}
              </div>
            </div>

            {/* Clinical Directives & Next Steps */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
              <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Info className="w-4 h-4 text-teal-400" />
                <span>{isSi ? "ක්ෂණික සායනික උපදෙස් සහ ආරක්ෂණ ක්‍රියාමාර්ග" : "Clinical Action Directives & Safety Netting"}</span>
              </div>
              <ul className="space-y-1.5 text-slate-300 pt-1">
                {(isSi ? analysisResult.clinical_directives_si : analysisResult.clinical_directives_en).map((dir, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-teal-400 font-bold">•</span>
                    <span className="leading-relaxed">{dir}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

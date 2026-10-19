/**
 * MedGuard Clinical Voice Engine
 * Real-time Speech-to-Text (STT) and Clinical Text-to-Speech (TTS)
 * Supports bilingual clinical interactions (Sinhala 'si-LK' and English 'en-US')
 * strictly zero emojis, medical-grade styling and accessible user states.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

/**
 * Strips markdown, citation tags, markdown links, and formatting
 * so that spoken clinical synthesis sounds natural and clear.
 */
export function cleanClinicalTextForSpeech(text: string): string {
  if (!text) return "";

  let cleaned = text;

  // Remove guideline citations like [Ref 1: NICE NG143] or [Ref 2] or [WHO 2023]
  cleaned = cleaned.replace(/\[Ref\s*[^\]]+\]/gi, " ");
  cleaned = cleaned.replace(/\[\s*(WHO|NICE|AHA|ACC|ADA|CDC|ICD-11)[^\]]*\]/gi, " ");
  cleaned = cleaned.replace(/\[\d+\]/g, " ");

  // Strip markdown image tags ![alt](url) and markdown links [text](url) -> keep text
  cleaned = cleaned.replace(/!\[([^\]]*)\]\([^)]*\)/g, "");
  cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]*\)/g, "$1");

  // Strip URLs
  cleaned = cleaned.replace(/https?:\/\/\S+/gi, "");

  // Strip markdown headers (e.g., ### Recommendation -> Recommendation)
  cleaned = cleaned.replace(/#{1,6}\s+/g, "");

  // Strip bold/italics markers
  cleaned = cleaned.replace(/[*_]{1,3}([^*_]+)[*_]{1,3}/g, "$1");

  // Strip code blocks and inline code
  cleaned = cleaned.replace(/```[\s\S]*?```/g, "");
  cleaned = cleaned.replace(/`([^`]+)`/g, "$1");

  // Strip markdown table rows (lines containing |)
  cleaned = cleaned.replace(/\|/g, " ");

  // Strip bullet markers (- or * or +) at start of lines
  cleaned = cleaned.replace(/^[\s*+-]+\s+/gm, "");

  // Normalize multiple spaces and newlines into natural pauses
  cleaned = cleaned.replace(/\s+/g, " ").trim();

  return cleaned;
}

/**
 * Backend voice synthesis helper
 * Falls back to server-side gTTS audio streaming audio/mpeg
 */
export async function synthesizeClinicalSpeechServer(
  text: string,
  language: string
): Promise<HTMLAudioElement> {
  const cleaned = cleanClinicalTextForSpeech(text);
  if (!cleaned) throw new Error("No readable text provided for voice synthesis");

  const normalizedLang = language === "si" || language.startsWith("si") ? "si-LK" : "en-US";

  const response = await fetch(`${API_BASE}/voice/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: cleaned,
      language: normalizedLang
    })
  });

  if (!response.ok) {
    const errorDetails = await response.json().catch(() => ({ detail: "Synthesis failed" }));
    throw new Error(errorDetails.detail || "Server voice synthesis failed");
  }

  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);

  // Clean up object URL when playback finishes
  audio.addEventListener("ended", () => {
    URL.revokeObjectURL(audioUrl);
  });
  audio.addEventListener("error", () => {
    URL.revokeObjectURL(audioUrl);
  });

  return audio;
}

/**
 * Clinical Voice Player Controller
 * Coordinates between client-side Web Speech Synthesis and backend audio streaming
 */
class VoicePlayerManager {
  private currentId: string | null = null;
  private activeAudio: HTMLAudioElement | null = null;
  private activeUtterance: SpeechSynthesisUtterance | null = null;
  private onEndCallbacks: Map<string, () => void> = new Map();

  public getCurrentId(): string | null {
    return this.currentId;
  }

  public isPlaying(id?: string): boolean {
    if (!this.currentId) return false;
    return id ? this.currentId === id : true;
  }

  public stop(): void {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      try {
        window.speechSynthesis.cancel();
      } catch {
        // Ignore
      }
    }

    if (this.activeAudio) {
      try {
        this.activeAudio.pause();
        this.activeAudio.currentTime = 0;
      } catch {
        // Ignore
      }
      this.activeAudio = null;
    }

    if (this.currentId && this.onEndCallbacks.has(this.currentId)) {
      const cb = this.onEndCallbacks.get(this.currentId);
      cb?.();
    }

    this.currentId = null;
    this.activeUtterance = null;
    this.onEndCallbacks.clear();
  }

  public async speak(
    id: string,
    rawText: string,
    language: string,
    callbacks?: {
      onStart?: () => void;
      onEnd?: () => void;
      onError?: (err: any) => void;
    }
  ): Promise<void> {
    // If clicking the currently playing message, toggle off / stop
    if (this.currentId === id) {
      this.stop();
      return;
    }

    this.stop();

    const cleaned = cleanClinicalTextForSpeech(rawText);
    if (!cleaned) return;

    this.currentId = id;
    if (callbacks?.onEnd) {
      this.onEndCallbacks.set(id, callbacks.onEnd);
    }

    const isSinhala = language === "si" || language.startsWith("si");

    // Sinhala synthesis: Browser Web Speech API rarely includes native Sinhala voices;
    // use the high-clarity server-side backend endpoint first.
    if (isSinhala) {
      try {
        callbacks?.onStart?.();
        const audio = await synthesizeClinicalSpeechServer(cleaned, "si-LK");
        this.activeAudio = audio;

        audio.onended = () => {
          if (this.currentId === id) {
            this.currentId = null;
            this.activeAudio = null;
            callbacks?.onEnd?.();
          }
        };

        audio.onerror = (e) => {
          if (this.currentId === id) {
            this.currentId = null;
            this.activeAudio = null;
            callbacks?.onError?.(e);
          }
        };

        await audio.play();
        return;
      } catch (serverErr) {
        // If server synthesis fails, try client synthesis as fallback
        this.fallbackClientSynthesis(id, cleaned, "si-LK", callbacks);
        return;
      }
    }

    // English synthesis: Attempt browser SpeechSynthesis first for zero-latency response
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      try {
        callbacks?.onStart?.();
        const utterance = new SpeechSynthesisUtterance(cleaned);
        utterance.lang = "en-US";
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        // Choose a clear English voice if available
        const voices = window.speechSynthesis.getVoices();
        const enVoice = voices.find(
          (v) => (v.lang.startsWith("en") || v.lang.includes("en-US")) && !v.name.includes("whisper")
        );
        if (enVoice) utterance.voice = enVoice;

        utterance.onend = () => {
          if (this.currentId === id) {
            this.currentId = null;
            this.activeUtterance = null;
            callbacks?.onEnd?.();
          }
        };

        utterance.onerror = (e) => {
          // If browser utterance failed, fallback to server audio
          this.fallbackServerSynthesis(id, cleaned, "en-US", callbacks);
        };

        this.activeUtterance = utterance;
        window.speechSynthesis.speak(utterance);
        return;
      } catch {
        // Fall back to server
      }
    }

    // Fallback if browser SpeechSynthesis unavailable
    await this.fallbackServerSynthesis(id, cleaned, "en-US", callbacks);
  }

  private fallbackClientSynthesis(
    id: string,
    text: string,
    lang: string,
    callbacks?: { onStart?: () => void; onEnd?: () => void; onError?: (err: any) => void }
  ) {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      try {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.onend = () => {
          if (this.currentId === id) {
            this.currentId = null;
            callbacks?.onEnd?.();
          }
        };
        utterance.onerror = (e) => {
          if (this.currentId === id) {
            this.currentId = null;
            callbacks?.onError?.(e);
          }
        };
        this.activeUtterance = utterance;
        window.speechSynthesis.speak(utterance);
        return;
      } catch (e) {
        callbacks?.onError?.(e);
      }
    }
    this.currentId = null;
    callbacks?.onEnd?.();
  }

  private async fallbackServerSynthesis(
    id: string,
    text: string,
    lang: string,
    callbacks?: { onStart?: () => void; onEnd?: () => void; onError?: (err: any) => void }
  ) {
    try {
      const audio = await synthesizeClinicalSpeechServer(text, lang);
      this.activeAudio = audio;

      audio.onended = () => {
        if (this.currentId === id) {
          this.currentId = null;
          this.activeAudio = null;
          callbacks?.onEnd?.();
        }
      };

      audio.onerror = (e) => {
        if (this.currentId === id) {
          this.currentId = null;
          this.activeAudio = null;
          callbacks?.onError?.(e);
        }
      };

      await audio.play();
    } catch (err) {
      this.currentId = null;
      callbacks?.onError?.(err);
    }
  }
}

export const clinicalVoicePlayer = new VoicePlayerManager();

/**
 * Checks if Speech Recognition is supported in the current browser.
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === "undefined") return false;
  return Boolean(
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition
  );
}

export interface SpeechRecognitionOptions {
  language: string; // 'si' | 'en' | 'si-LK' | 'en-US'
  onResult: (transcript: string, isFinal: boolean) => void;
  onError?: (error: string) => void;
  onEnd?: () => void;
}

/**
 * Manages Web Speech Recognition lifecycle with bilingual language targeting.
 */
export class ClinicalSpeechRecognizer {
  private recognition: any = null;
  private isListeningState: boolean = false;

  constructor(private options: SpeechRecognitionOptions) {}

  public isSupported(): boolean {
    return isSpeechRecognitionSupported();
  }

  public get isListening(): boolean {
    return this.isListeningState;
  }

  public start(): boolean {
    if (!this.isSupported()) {
      this.options.onError?.("Speech recognition not supported in this browser");
      return false;
    }

    const SpeechRecognitionClass =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    try {
      this.recognition = new SpeechRecognitionClass();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;

      const langCode =
        this.options.language === "si" || this.options.language.startsWith("si")
          ? "si-LK"
          : "en-US";
      this.recognition.lang = langCode;

      this.recognition.onstart = () => {
        this.isListeningState = true;
      };

      this.recognition.onresult = (event: any) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const result = event.results[i];
          const transcript = result[0].transcript;
          if (result.isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        if (finalTranscript) {
          this.options.onResult(finalTranscript, true);
        } else if (interimTranscript) {
          this.options.onResult(interimTranscript, false);
        }
      };

      this.recognition.onerror = (event: any) => {
        this.isListeningState = false;
        if (event.error !== "no-speech") {
          this.options.onError?.(event.error);
        }
      };

      this.recognition.onend = () => {
        this.isListeningState = false;
        this.options.onEnd?.();
      };

      this.recognition.start();
      return true;
    } catch (err: any) {
      this.isListeningState = false;
      this.options.onError?.(err?.message || "Failed to start speech recognition");
      return false;
    }
  }

  public stop(): void {
    if (this.recognition && this.isListeningState) {
      try {
        this.recognition.stop();
      } catch {
        // Ignore
      }
      this.isListeningState = false;
    }
  }
}

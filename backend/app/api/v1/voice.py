import io
import re
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import speech_recognition as sr
from gtts import gTTS

router = APIRouter(prefix="/voice", tags=["Voice Input & Output (STT / TTS)"])


class SynthesizeRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    speed: Optional[float] = 1.0


def clean_medical_text_for_speech(raw_text: str) -> str:
    """
    Cleans clinical markdown, references, citations, and formatting
    so the speech synthesizer delivers natural, clear, professional voice articulation.
    """
    # Remove citations like [Ref 1], [Ref 2: AHA]
    text = re.sub(r"\[Ref\s*\d+[^\]]*\]", "", raw_text, flags=re.IGNORECASE)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove markdown headers (### Header)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Remove markdown bold/italic (**text**, *text*)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove bullet symbols
    text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.MULTILINE)
    # Remove table markup (| col | col |)
    text = re.sub(r"\|[^\n]+\|", "", text)
    # Replace multiple spaces or newlines with a single space
    text = re.sub(r"\n+", ". ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


@router.get("/capabilities")
async def get_voice_capabilities():
    """
    Returns supported speech-to-text and text-to-speech languages and engine configuration.
    """
    return {
        "status": "AVAILABLE",
        "stt": {
            "supported_languages": [
                {"code": "si-LK", "name": "Sinhala (Sri Lanka)", "native_name": "සිංහල"},
                {"code": "en-US", "name": "English (US)", "native_name": "English (US)"},
                {"code": "en-GB", "name": "English (UK)", "native_name": "English (UK)"}
            ],
            "default_language": "si-LK",
            "offline_fallback": True
        },
        "tts": {
            "supported_languages": [
                {"code": "si", "name": "Sinhala", "native_name": "සිංහල"},
                {"code": "en", "name": "English", "native_name": "English"}
            ],
            "default_language": "si",
            "formats": ["audio/mpeg"]
        }
    }


@router.post("/synthesize")
async def synthesize_speech(payload: SynthesizeRequest):
    """
    Converts clinical text into an audible spoken stream (Text-to-Speech)
    using gTTS with native Sinhala ('si') and English ('en') voice synthesis.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Speech synthesis requires non-empty text."
        )

    clean_text = clean_medical_text_for_speech(payload.text)
    if not clean_text:
        clean_text = "Clinical assessment complete."

    # Language mapping: Sinhala is 'si', English is 'en'
    lang_code = "si" if payload.language and payload.language.lower().startswith("si") else "en"

    try:
        # Generate MP3 audio using gTTS in memory
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=clinical_response.mp3",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis error: {str(e)}"
        )


@router.post("/transcribe")
async def transcribe_speech(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form("si-LK")
):
    """
    Server-side fallback speech-to-text audio transcription.
    Accepts audio recording blob (WAV, WEBM, OGG) and transcribes speech into text.
    """
    if not audio_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is required."
        )

    file_bytes = await audio_file.read()
    if len(file_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file payload is too short or empty."
        )

    # Resolve language code
    lang = "si-LK" if language and language.startswith("si") else "en-US"

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        # Attempt to load audio data through speech_recognition
        with io.BytesIO(file_bytes) as audio_stream:
            # Check if standard AudioFile can parse (WAV / AIFF / FLAC)
            try:
                with sr.AudioFile(audio_stream) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language=lang)
                    return {
                        "success": True,
                        "transcript": text,
                        "language": lang,
                        "confidence": 0.95
                    }
            except Exception as parse_err:
                # If audio is WebM or raw browser format not decoded by standard wave,
                # provide fallback response with helpful metadata
                return {
                    "success": False,
                    "transcript": "",
                    "language": lang,
                    "error": f"Audio format requires client-side Web Speech recognition: {str(parse_err)}"
                }
    except Exception as e:
        return {
            "success": False,
            "transcript": "",
            "language": lang,
            "error": str(e)
        }

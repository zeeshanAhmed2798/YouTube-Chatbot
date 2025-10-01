from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import requests
import json

def translate_to_english(text: str) -> str:
    """Translate large Hindi/Urdu text to English safely (handles long text)."""
    if not text.strip():
        return ""

    def translate_chunk(chunk: str) -> str:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': 'en',
            'dt': 't',
            'q': chunk
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            try:
                result = response.json()
                if result and len(result) > 0 and result[0]:
                    translated = ''.join([item[0] for item in result[0] if item[0]])
                    return translated
            except Exception:
                pass
        return chunk

    # Split into safe chunks (Google fails > 2000 chars)
    chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
    translated_parts = []

    for chunk in chunks:
        translated_chunk = translate_chunk(chunk)
        translated_parts.append(translated_chunk)

    translated_text = " ".join(translated_parts).strip()
    
    # Quality check
    english_chars = sum(1 for c in translated_text if c.isascii() and c.isalpha())
    total_chars = sum(1 for c in translated_text if c.isalpha())
    quality_ratio = english_chars / total_chars if total_chars > 0 else 0
    
    if total_chars > 0 and quality_ratio < 0.3:
        return text
    else:
        return translated_text

def get_transcript(video_id: str) -> str:
    """Get YouTube transcript with translation to English"""
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        hindi_fetched = None
        english_fetched = None
        english_transcript_obj = None

        for t in transcript_list:
            lang_code = getattr(t, "language_code", getattr(t, "language", "unknown"))
            if lang_code == "hi":
                hindi_fetched = t.fetch()
            elif lang_code == "en":
                english_transcript_obj = t
                english_fetched = t.fetch()

        if hindi_fetched:
            transcript_text = " ".join([s.text for s in getattr(hindi_fetched, "snippets", hindi_fetched)])
            translated_transcript = translate_to_english(transcript_text)
            return translated_transcript
        elif english_fetched:
            transcript_text = " ".join([s.text for s in getattr(english_fetched, "snippets", english_fetched)])
            return transcript_text
        else:
            return "No Hindi or English transcript found."

    except (NoTranscriptFound, TranscriptsDisabled) as e:
        return f"Transcript error: {str(e)}"
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

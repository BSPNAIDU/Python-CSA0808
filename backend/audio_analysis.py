import librosa
import numpy as np

FILLER_WORDS = ["um", "uh", "like", "you know", "actually", "basically"]

def analyze_audio(audio_path, transcript):
    y, sr = librosa.load(audio_path)

    duration = librosa.get_duration(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    avg_rms = float(np.mean(rms))

    words = transcript.lower().split()
    word_count = len(words)

    filler_count = 0
    for word in FILLER_WORDS:
        filler_count += transcript.lower().count(word)

    speech_rate = round(word_count / duration * 60, 2) if duration > 0 else 0

    silent_parts = librosa.effects.split(y, top_db=30)
    active_duration = sum((end - start) / sr for start, end in silent_parts)
    pause_ratio = round(((duration - active_duration) / duration) * 100, 2) if duration > 0 else 0

    return {
        "duration": round(duration, 2),
        "word_count": word_count,
        "filler_count": filler_count,
        "speech_rate": speech_rate,
        "rms_energy": round(avg_rms, 4),
        "pause_ratio": pause_ratio
    }
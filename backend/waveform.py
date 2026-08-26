import librosa
import librosa.display
import matplotlib.pyplot as plt
import os

def generate_waveform(audio_path):

    y, sr = librosa.load(audio_path)

    plt.figure(figsize=(10,3))

    librosa.display.waveshow(y, sr=sr)

    plt.title("Audio Waveform")

    plt.xlabel("Time")

    plt.ylabel("Amplitude")

    os.makedirs("reports", exist_ok=True)

    image_path = "reports/waveform.png"

    plt.savefig(image_path)

    plt.close()

    return image_path    
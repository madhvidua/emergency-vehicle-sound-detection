import os
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import argparse


def normalize_samples(samples):
    samples = np.array(samples, dtype=float)
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        return samples / max_val
    return samples


def plot_waveform(audio_chunk, chunk_name):
    samples = np.array(audio_chunk.get_array_of_samples())
    normalized_samples = normalize_samples(samples)

    # Downsample for visualization
    downsample_factor = max(1, len(normalized_samples) // 10000)  # Adjust this value if needed
    normalized_samples = normalized_samples[::downsample_factor]

    plt.figure(figsize=(10, 4))
    plt.plot(normalized_samples)
    plt.title(f"Waveform of {chunk_name}")
    plt.xlabel("Sample")
    plt.ylabel("Normalized Amplitude")
    plt.ylim([-1, 1])  # Normalized range for better visualization
    plt.grid(True)
    plt.savefig(f"{chunk_name}.png")
    plt.close()


def generate_waveforms(input_folder):
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".wav"):
            file_path = os.path.join(input_folder, file_name)
            audio_chunk = AudioSegment.from_wav(file_path)
            base_name = os.path.splitext(file_name)[0]
            chunk_name = os.path.join(input_folder, base_name)
            plot_waveform(audio_chunk, chunk_name)
            print(f"Generated waveform for {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate waveforms for WAV files in a folder.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing WAV files")

    args = parser.parse_args()
    generate_waveforms(args.input_folder)
import os
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment


class WaveformGenerator:
    @staticmethod
    def normalize_samples(samples):
        return samples / 10946.0

    def plot_waveform(self, audio_chunk, chunk_name):
        samples = np.array(audio_chunk.get_array_of_samples())
        normalized_samples = self.normalize_samples(samples)

        plt.figure(figsize=(10, 4))
        plt.plot(normalized_samples)
        plt.title(f"Waveform of {chunk_name}")
        plt.xlabel("Sample")
        plt.ylabel("Normalized Amplitude")
        plt.ylim([-1, 1])
        plt.grid(True)
        plt.savefig(f"{chunk_name}.png")
        plt.close()

    def generate_waveforms(self, input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".wav"):
                file_path = os.path.join(input_folder, file_name)
                audio_chunk = AudioSegment.from_wav(file_path)
                base_name = os.path.splitext(file_name)[0]
                chunk_name = os.path.join(output_folder, base_name)
                self.plot_waveform(audio_chunk, chunk_name)
                print(f"Generated waveform for {file_name}")

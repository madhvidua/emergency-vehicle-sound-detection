import os
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import argparse

DATA_BASE_FOLDER = 'data'
DATA_VISUALIZATION_BASE_FOLDER = 'data-visualization'


class PathManager:
    def __init__(self, base_folder=DATA_BASE_FOLDER, visualization_base_folder=DATA_VISUALIZATION_BASE_FOLDER):
        self.base_folder = base_folder
        self.visualization_base_folder = visualization_base_folder

    def get_output_folder(self, input_folder):
        path_segments = input_folder.split(os.sep)

        if path_segments[0] == '.' and len(path_segments) > 1 and path_segments[1] == self.base_folder:
            path_segments[1] = self.visualization_base_folder
        elif path_segments[0] == self.base_folder:
            path_segments[0] = self.visualization_base_folder

        output_folder = os.sep.join(path_segments)
        os.makedirs(output_folder, exist_ok=True)

        return output_folder


class WaveformGenerator:
    def __init__(self, path_manager):
        self.path_manager = path_manager

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

    def generate_waveforms(self, input_folder):
        output_folder = self.path_manager.get_output_folder(input_folder)
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".wav"):
                file_path = os.path.join(input_folder, file_name)
                audio_chunk = AudioSegment.from_wav(file_path)
                base_name = os.path.splitext(file_name)[0]
                chunk_name = os.path.join(output_folder, base_name)
                self.plot_waveform(audio_chunk, chunk_name)
                print(f"Generated waveform for {file_name}")


def main():
    parser = argparse.ArgumentParser(description="Generate waveforms for WAV files in a folder.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing WAV files")

    args = parser.parse_args()

    path_manager = PathManager()
    waveform_generator = WaveformGenerator(path_manager)
    waveform_generator.generate_waveforms(args.input_folder)


if __name__ == "__main__":
    main()

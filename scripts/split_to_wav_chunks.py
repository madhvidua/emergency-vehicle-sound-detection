import os
from pydub import AudioSegment
import datetime
import argparse
import numpy as np
import matplotlib.pyplot as plt

SUPPORTED_AUDIO_FORMATS = ['.m4a', '.wav', '.mp3', '.flac']


def format_duration(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    minutes = minutes % 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}h{minutes}m"
    elif minutes > 0:
        return f"{minutes}m{seconds}s"
    else:
        return f"{seconds}s"


def split_audio(audio, chunk_length_ms, output_folder):
    total_length_ms = len(audio)
    chunks = []

    for i in range(0, total_length_ms, chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunks.append(chunk)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    elif len(os.listdir(output_folder)) > 0:
        print(f"Skipping {output_folder} because it is not empty.")
        return

    for j, chunk in enumerate(chunks):
        actual_duration_ms = len(chunk)
        duration = format_duration(actual_duration_ms)
        chunk_name = os.path.join(output_folder, f"chunk_{j + 1}_{duration}")
        chunk.export(f"{chunk_name}.wav", format="wav")
        print(f"Exported {chunk_name}.wav")


def max_value(audio):
    samples = np.array(audio.get_array_of_samples())
    samples = np.array(samples, dtype=float)
    return np.max(np.abs(samples))


def process_file(file_path, chunk_length_ms, input_folder):
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} is not a file.")
        return

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in SUPPORTED_AUDIO_FORMATS:
        print(f"Error: {file_path} is not a supported audio file.")
        return

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    duration = format_duration(chunk_length_ms)
    output_folder = os.path.join(input_folder, f"{base_name}_{duration}")
    chunk_name = os.path.join(input_folder, base_name)
    audio = AudioSegment.from_file(file_path)
    config_file = os.path.join(input_folder, f"{base_name}.config")
    with open(config_file, 'w') as config:
        config.write(f"{file_path},{max_value(audio)}")
    split_audio(file_path, chunk_length_ms, output_folder)

def process_all_files(input_folder, chunk_length_ms):
    for file_name in os.listdir(input_folder):
        if file_name.endswith(tuple(SUPPORTED_AUDIO_FORMATS)):
            file_path = os.path.join(input_folder, file_name)
            process_file(file_path, chunk_length_ms, input_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split audio files into chunks.")
    parser.add_argument("--input_folder", type=str, default="data", help="Folder containing audio files")
    parser.add_argument("--chunk_length_ms", type=int, default=3600000, help="Length of each chunk in milliseconds")
    parser.add_argument("--input_file", type=str, help="Specific audio file to split")

    args = parser.parse_args()

    if args.input_file:
        process_file(args.input_file, args.chunk_length_ms, os.path.dirname(args.input_file))
    else:
        process_all_files(args.input_folder, args.chunk_length_ms)

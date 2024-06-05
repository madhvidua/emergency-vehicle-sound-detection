import os
from pydub import AudioSegment
import argparse

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

def split_audio(file_path, chunk_length_ms, output_folder):
    audio = AudioSegment.from_file(file_path)
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
        duration = format_duration(len(chunk))
        chunk_name = os.path.join(output_folder, f"chunk_{j + 1}_{duration}")
        chunk.export(f"{chunk_name}.wav", format="wav")
        print(f"Exported {chunk_name}.wav")

def process_all_files(input_folder="data", chunk_length_ms=3600000):
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".m4a"):
            file_path = os.path.join(input_folder, file_name)
            base_name = os.path.splitext(file_name)[0]
            duration = format_duration(chunk_length_ms)
            output_folder = os.path.join(input_folder, f"{base_name}_{duration}")
            split_audio(file_path, chunk_length_ms, output_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split audio files into chunks.")
    parser.add_argument("--input_folder", type=str, default="data", help="Folder containing audio files")
    parser.add_argument("--chunk_length_ms", type=int, default=3600000, help="Length of each chunk in milliseconds")

    args = parser.parse_args()
    process_all_files(args.input_folder, args.chunk_length_ms)

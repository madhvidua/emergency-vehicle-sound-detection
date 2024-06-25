import os
from pydub import AudioSegment
import argparse

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


class AudioSplitter:
    def __init__(self, chunk_length_ms, output_folder):
        self.chunk_length_ms = chunk_length_ms
        self.output_folder = output_folder

    def split_audio(self, file_path):
        print(f"Processing file: {file_path}")
        try:
            audio = AudioSegment.from_file(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return

        total_length_ms = len(audio)
        chunks = []

        for i in range(0, total_length_ms, self.chunk_length_ms):
            chunk = audio[i:i + self.chunk_length_ms]
            chunks.append(chunk)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        duration = format_duration(self.chunk_length_ms)
        output_folder = os.path.join(self.output_folder, f"{base_name}_{duration}")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        elif len(os.listdir(output_folder)) > 0:
            print(f"Skipping {output_folder} because it is not empty.")
            return

        for j, chunk in enumerate(chunks):
            actual_duration_ms = len(chunk)
            duration = format_duration(actual_duration_ms)
            chunk_name = os.path.join(output_folder, f"chunk_{j + 1}_{duration}.wav")
            try:
                chunk.export(chunk_name, format="wav")
                print(f"Exported {chunk_name}")
            except Exception as e:
                print(f"Error exporting {chunk_name}: {e}")

    def process_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} is not a file.")
            return

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in SUPPORTED_AUDIO_FORMATS:
            print(f"Error: {file_path} is not a supported audio file.")
            return

        self.split_audio(file_path)

    def process_all_files(self, input_folder):
        for file_name in os.listdir(input_folder):
            if file_name.lower().endswith(tuple(SUPPORTED_AUDIO_FORMATS)):
                file_path = os.path.join(input_folder, file_name)
                self.process_file(file_path)


def main():
    parser = argparse.ArgumentParser(description="Split audio files into chunks.")
    parser.add_argument("--input_folder", type=str, default="data", help="Folder containing audio files")
    parser.add_argument("--chunk_length_ms", type=int, default=3000, help="Length of each chunk in milliseconds")
    parser.add_argument("--input_file", type=str, help="Specific audio file to split")

    args = parser.parse_args()

    splitter = AudioSplitter(args.chunk_length_ms, args.input_folder)

    if args.input_file:
        splitter.process_file(args.input_file)
    else:
        splitter.process_all_files(args.input_folder)


if __name__ == "__main__":
    main()

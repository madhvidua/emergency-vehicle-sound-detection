import os
from pydub import AudioSegment
from tqdm import tqdm
from .utils import format_duration

SUPPORTED_AUDIO_FORMATS = ['.m4a', '.wav', '.mp3', '.flac']
OUTPUT_AUDIO_FILE_FORMAT = 'wav'


class AudioSplitter:
    def __init__(self, chunk_length_ms, output_folder):
        self.chunk_length_ms = chunk_length_ms
        self.output_folder = output_folder

    def is_folder_empty(self, folder):
        return all(f.startswith('.') for f in os.listdir(folder))

    def split_audio(self, file_path):
        print(f"Processing file: {file_path}")
        try:
            audio = AudioSegment.from_file(file_path)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return

        total_length_ms = len(audio)
        chunks = []
        desired_chunk_duration = format_duration(self.chunk_length_ms)

        for i in range(0, total_length_ms, self.chunk_length_ms):
            chunk = audio[i:i + self.chunk_length_ms]
            chunks.append(chunk)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        duration = format_duration(self.chunk_length_ms)
        output_folder = os.path.join(self.output_folder, f"{base_name}_{duration}")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        elif not self.is_folder_empty(output_folder):
            print(f"Skipping {output_folder} because it is not empty.")
            return

        for j, chunk in tqdm(enumerate(chunks), total=len(chunks)):
            actual_duration_ms = len(chunk)
            duration = format_duration(actual_duration_ms)
            chunk_name = os.path.join(output_folder,
                                      f"{base_name}_{duration}_chunk_{j + 1}_{duration}.{OUTPUT_AUDIO_FILE_FORMAT}")
            if duration == desired_chunk_duration:
                try:
                    chunk.export(chunk_name, format=OUTPUT_AUDIO_FILE_FORMAT)
                except Exception as e:
                    print(f"Error exporting {chunk_name}: {e}")
            else:
                print(f"Skipping creating chunk {chunk_name} because it does not match the desired length of "
                      f"{desired_chunk_duration}. Actual length is found as {duration}.")

    def process_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} is not a file.")
            return

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in SUPPORTED_AUDIO_FORMATS:
            print(f"Error: {file_path} is not a supported audio file.")
            return

        self.split_audio(file_path)
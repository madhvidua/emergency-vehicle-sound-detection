import argparse
from .audio_splitter import AudioSplitter

def main():
    parser = argparse.ArgumentParser(description="Split audio files into chunks.")
    parser.add_argument("--output_folder", type=str, default="data/processed", help="Output folder for processed audio files")
    parser.add_argument("--chunk_length_ms", type=int, default=3000, help="Length of each chunk in milliseconds")
    parser.add_argument("--input_file", type=str, help="Specific audio file to split")

    args = parser.parse_args()

    splitter = AudioSplitter(args.chunk_length_ms, args.output_folder)
    splitter.process_file(args.input_file)


# python -m src.data.audio_splitter.main --input_folder data/raw --chunk_length_ms 3000 --input_file data/raw/Sample_1.m4a
if __name__ == "__main__":
    main()

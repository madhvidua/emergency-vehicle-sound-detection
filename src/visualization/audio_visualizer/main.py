import argparse
from .waveform_generator import WaveformGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate waveforms for WAV files in a folder.")
    parser.add_argument("--input_folder", type=str, required=True, help="Folder containing WAV files")
    parser.add_argument("--output_folder", type=str, required=True, help="Folder containing visualization of input audio files.")

    args = parser.parse_args()

    waveform_generator = WaveformGenerator()
    waveform_generator.generate_waveforms(args.input_folder, args.output_folder)


# python -m src.visualization.audio_visualizer.main --input_folder data/processed/Sample_1_3s --output_folder data/visualized/Sample_1_3s
if __name__ == "__main__":
    main()

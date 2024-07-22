import argparse

import config
from src.features.audio_embedding.audio_data import AudioDataFactory
from src.features.audio_embedding.audio_embedder import VGGishAudioEmbedder
from src.features.audio_embedding.embedding import Embedding
from src.features.audio_embedding.retriever import EmbeddingRetriever
from src.models.stats.stats_printer import DatasetConfig, ClassificationStatPrinter
from src.models.zero_shot_vggish.classifier import ZeroShotVGGishClassifier


def main():
    parser = argparse.ArgumentParser(description="Zero shot classification of siren and nosiren audio dataset using VGGish")
    parser.add_argument('--search_dataset', type=str, required=True, help="Path to the folder containing the data set to search in.")
    parser.add_argument('--query_audio_path', type=str, required=True, help="Path to the query audio file for retrieval.")
    parser.add_argument('--similarity_thresholds', type=float, nargs='+', required=True,
                        help="List of similarity thresholds to base the classification on.")
    parser.add_argument('--chunk_length', type=int, choices=[1, 3], required=True, help="Length of the audio chunks in seconds (1 or 3)")
    parser.add_argument('--replace_existing', action='store_true', help="Replace existing embedding file if it exists")

    args = parser.parse_args()

    dataset_config = DatasetConfig(
        'siren',
        'nosiren',
        f"{config.DATA_DIR}/test_labeled/siren",
        f"{config.DATA_DIR}/test_labeled/nosiren",
        f"{config.OUTPUT_DIR}/vggish_zero_shot",
        f"{config.EMBEDDINGS_DIR}/vggish_zero_shot.pkl"
    )

    audio_data = AudioDataFactory.create_audio_data(args.chunk_length, args.search_dataset)
    embedding = Embedding(audio_data, dataset_config.embeddings_filepath, args.replace_existing)
    embedder = VGGishAudioEmbedder(audio_data)
    retriever = EmbeddingRetriever(audio_data, embedder, embedding)
    stat_printer = ClassificationStatPrinter(dataset_config)

    classifier = ZeroShotVGGishClassifier(
        audio_data=audio_data,
        embedding=embedding,
        embedder=embedder,
        retriever=retriever,
        stat_printer=stat_printer,
        force_refresh_embeddings=args.replace_existing
    )

    classifier.run(args.query_audio_path, args.similarity_thresholds)


if __name__ == "__main__":
    main()

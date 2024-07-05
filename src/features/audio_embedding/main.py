import torch
import numpy as np
import argparse
from .audio_data import AudioDataFactory
from .audio_embedder import VGGishAudioEmbedder
from .embedding import Embedding
from .retriever import EmbeddingRetriever


def main():
    parser = argparse.ArgumentParser(description="Audio Embedding and Retrieval")
    parser.add_argument('--audio_folder', type=str, required=True, help="Path to the folder containing audio files")
    parser.add_argument('--embedding_file', type=str, required=True, help="Path to the file to store/load embeddings")
    parser.add_argument('--chunk_length', type=int, choices=[1, 3], required=True,
                        help="Length of the audio chunks in seconds (1 or 3)")
    parser.add_argument('--query_audio_path', type=str, default=None,
                        help="Path to the query audio file for retrieval. If not provided, retrieval will be skipped.")
    parser.parse_args()
    parser.add_argument('--replace_existing', action='store_true', help="Replace existing embedding file if it exists")

    args = parser.parse_args()

    audio_data = AudioDataFactory.create_audio_data(args.chunk_length, args.audio_folder)

    embedding = Embedding(audio_data, args.embedding_file, replace_existing=args.replace_existing)
    embedder = VGGishAudioEmbedder(audio_data)
    retriever = EmbeddingRetriever(audio_data, embedder, embedding)

    if not embedding.embeddings_exist() or args.replace_existing:
        embeddings_list = embedder.generate_embeddings()
        embedding.store_embeddings(embeddings_list)
    else:
        print(f"The embedding file '{args.embedding_file}' already exists. Skipping embedding computation.")

    if args.query_audio_path is not None:
        with torch.no_grad():
            query_embedding = embedder.generate_embedding(args.query_audio_path).cpu().numpy().squeeze()

            try:
                similarities, filtered_embeddings = retriever.find_similar_embeddings(query_embedding)
                similarity_indices = np.argsort(similarities)[::-1]

                similarity_threshold = 0.90
                print(f"Audio files with similarity >= {similarity_threshold * 100}%:")

                found = False
                for index in similarity_indices:
                    similarity_score = similarities[index]
                    if similarity_score >= similarity_threshold:
                        path, _ = filtered_embeddings[index]
                        print(f"Audio file: {path}, Similarity score: {similarity_score}")
                        found = True
                    else:
                        break  # Since the list is sorted in descending order, we can break the loop once we drop below the threshold

                if not found:
                    print("No audio files with similarity >= 90% found.")

            except ValueError as e:
                print(f"Error: {e}")
    else:
        print("Query audio path not provided, skipping retrieval.")


# python -m src.features.audio_embedding.main --audio_folder data/processed/Sample_4_3s --embedding_file  embeddings/embeddings_Sample_4_3s.pkl
#                                             --chunk_length 3 --query_audio_path data/processed/Sample_4_3s/Sample_4_3s_chunk_6234_3s.wav
if __name__ == "__main__":
    main()

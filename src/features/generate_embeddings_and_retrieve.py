import os
import pickle
import torch
import numpy as np
import argparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from tqdm import tqdm
from abc import ABC, abstractmethod


class AudioData(ABC):
    def __init__(self, audio_folder):
        self.audio_folder = audio_folder
        self.audio_paths = self.get_audio_paths()

    def get_audio_paths(self):
        return sorted(
            [os.path.join(self.audio_folder, file) for file in os.listdir(self.audio_folder) if file.endswith('.wav')])

    @abstractmethod
    def get_chunk_length_seconds(self):
        pass

    @abstractmethod
    def get_expected_embedding_dimension(self):
        pass


class ThreeSecondAudioData(AudioData):
    __CHUNK_LENGTH_SECONDS = 3
    __EXPECTED_EMBEDDING_DIMENSION = (3, 128)

    def __init__(self, audio_folder):
        super().__init__(audio_folder)

    def get_chunk_length_seconds(self):
        return self.__CHUNK_LENGTH_SECONDS

    def get_expected_embedding_dimension(self):
        return self.__EXPECTED_EMBEDDING_DIMENSION


class OneSecondAudioData(AudioData):
    __CHUNK_LENGTH_SECONDS = 1
    __EXPECTED_EMBEDDING_DIMENSION = (1, 128)

    def __init__(self, audio_folder):
        super().__init__(audio_folder)

    def get_chunk_length_seconds(self):
        return self.__CHUNK_LENGTH_SECONDS

    def get_expected_embedding_dimension(self):
        return self.__EXPECTED_EMBEDDING_DIMENSION


class AudioDataFactory:
    @staticmethod
    def create_audio_data(chunk_length, audio_folder):
        if chunk_length == 1:
            return OneSecondAudioData(audio_folder)
        elif chunk_length == 3:
            return ThreeSecondAudioData(audio_folder)
        else:
            raise ValueError("Invalid chunk length. Only 1 or 3 seconds are supported.")


class Embedding:
    def __init__(self, audio_data, embedding_file, replace_existing=False):
        self.audio_data = audio_data
        self.embedding_file = embedding_file
        self.replace_existing = replace_existing
        self.embeddings_list = None

    def load_embeddings(self):
        if self.embeddings_exist():
            with open(self.embedding_file, 'rb') as f:
                self.embeddings_list = pickle.load(f)
        else:
            print(f"Embedding file '{self.embedding_file}' does not exist.")

    def store_embeddings(self, embeddings_list):
        if self.replace_existing or not self.embeddings_exist():
            with open(self.embedding_file, 'wb') as f:
                pickle.dump(embeddings_list, f)
            self.embeddings_list = embeddings_list
        else:
            print(
                f"Embedding file '{self.embedding_file}' already exists and replace_existing is False. Skipping storage.")

    def embeddings_exist(self):
        return os.path.exists(self.embedding_file)


class AudioEmbedder(ABC):
    def __init__(self, audio_data, device=None):
        self.audio_data = audio_data
        if device is None:
            device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.device = device
        self.load_model()

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def generate_embedding(self, audio_path):
        pass

    def generate_embeddings(self):
        embeddings_list = []
        for path in tqdm(self.audio_data.audio_paths):
            with torch.no_grad():
                embeddings = self.generate_embedding(path)
            embeddings_list.append((path, embeddings.cpu().numpy().squeeze()))
        return embeddings_list


class VGGishAudioEmbedder(AudioEmbedder):
    MODEL_NAME = 'harritaylor/torchvggish'
    MODEL_TYPE = 'vggish'

    def load_model(self):
        self.model = torch.hub.load(self.MODEL_NAME, self.MODEL_TYPE).to(self.device)
        self.model.postprocess = False
        self.model.device = self.device
        self.model.eval()

    def generate_embedding(self, audio_path):
        return self.model(audio_path).to(self.device)


class EmbeddingRetriever:
    def __init__(self, audio_data, embedder, embedding):
        self.audio_data = audio_data
        self.embedder = embedder
        self.embedding = embedding

    def find_similar_embeddings(self, query_embedding):
        if self.embedding.embeddings_list is None:
            self.embedding.load_embeddings()

        stored_embeddings = self.embedding.embeddings_list

        filtered_embeddings = []
        expected_dimension = self.audio_data.get_expected_embedding_dimension()
        for item in stored_embeddings:
            if isinstance(item, tuple) and len(item) == 2:
                path, se = item
                if se.shape == expected_dimension:
                    normalized_embedding = normalize(np.mean(se, axis=0).reshape(1, -1))[0]
                    filtered_embeddings.append((path, normalized_embedding))
            else:
                print(f"Invalid item format: {item}")

        if not filtered_embeddings:
            raise ValueError("No embeddings with the required shape were found.")

        query_embedding = normalize(np.mean(query_embedding, axis=0).reshape(1, -1))[0]
        similarities = cosine_similarity([query_embedding], [embedding for _, embedding in filtered_embeddings])
        return similarities[0], filtered_embeddings


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

    # TODO: Bug - This if is preventing an overwrite of the embeddings file
    if not embedding.embeddings_exist():
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


if __name__ == "__main__":
    main()

import logging

import numpy as np
import torch

from src.models.abstract_audio_classifier import AbstractAudioClassifier
from src.utils.file_manager import FileManager

logging.basicConfig(level=logging.INFO)


class ZeroShotVGGishClassifier(AbstractAudioClassifier):
    def __init__(self, audio_data, embedding, embedder, retriever, stat_printer, force_refresh_embeddings):
        super().__init__(force_refresh_embeddings)
        self.audio_data = audio_data
        self.embedding = embedding
        self.embedder = embedder
        self.retriever = retriever
        self.stat_printer = stat_printer

    def run(self, query_audio_path, similarity_thresholds):
        with torch.no_grad():
            self.generate_embeddings()
            query_embedding = self.embedder.generate_embedding(query_audio_path).cpu().numpy().squeeze()
            similarities, filtered_embeddings = self.retriever.find_similar_embeddings(query_embedding)
            similarity_indices = np.argsort(similarities)[::-1]

            FileManager.create_directory(directory=self.stat_printer.dataset_config.output_basepath, allow_existing=True, allow_non_empty=True)

            for threshold in similarity_thresholds:
                self.classify(similarity_indices, similarities, filtered_embeddings, query_audio_path, threshold)
                self.print_performance_stats(query_audio_path, threshold)

    def generate_embeddings(self):
        if not self.embedding.embeddings_exist() or self.force_refresh_embeddings:
            embeddings_list = self.embedder.generate_embeddings()
            self.embedding.store_embeddings(embeddings_list)
        else:
            logging.info("The embedding file already exists. Skipping embedding computation.")

    def classify(self, similarity_indices, similarities, filtered_embeddings, query_audio_path, similarity_threshold):
        try:
            logging.info(f"Using similarity threshold as {similarity_threshold * 100}%")

            first_class_output_filepath, second_class_output_filepath = self.stat_printer.get_output_filepaths(query_audio_path, similarity_threshold)

            with open(first_class_output_filepath, 'w') as first_class_file, open(second_class_output_filepath, 'w') as second_class_file:
                for i, index in enumerate(similarity_indices):
                    similarity_score = similarities[index]
                    path, _ = filtered_embeddings[index]
                    if similarity_score >= similarity_threshold:
                        first_class_file.write(f"{path},{similarity_score}\n")
                    else:
                        self._write_remaining_paths(second_class_file, similarity_indices[i:], filtered_embeddings, similarities)
                        break

        except ValueError as e:
            logging.error(f"Error: {e}")

    @staticmethod
    def _write_remaining_paths(file, indices, embeddings, similarities):
        for idx in indices:
            path, _ = embeddings[idx]
            similarity_score = similarities[idx]
            file.write(f"{path},{similarity_score}\n")

    def print_performance_stats(self, query_audio_path, similarity_threshold):
        self.stat_printer.print_performance_stats(query_audio_path, similarity_threshold)

from abc import ABC, abstractmethod


class AbstractAudioClassifier(ABC):

    def __init__(self, force_refresh_embeddings):
        self.force_refresh_embeddings = force_refresh_embeddings

    @abstractmethod
    def run(self, query_audio_path, similarity_threshold):
        pass

    @abstractmethod
    def generate_embeddings(self):
        pass

    @abstractmethod
    def classify(self, similarity_indices, similarities, filtered_embeddings, query_audio_path, similarity_threshold):
        pass

    @abstractmethod
    def print_performance_stats(self, query_audio_path, similarity_threshold):
        pass

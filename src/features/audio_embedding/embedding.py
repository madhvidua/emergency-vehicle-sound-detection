import os
import pickle


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

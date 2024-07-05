import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize


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

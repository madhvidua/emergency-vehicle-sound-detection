from abc import ABC, abstractmethod

import torch
from tqdm import tqdm

import config


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
    def load_model(self):
        self.model = torch.hub.load(config.MODEL_NAME, config.MODEL_TYPE).to(self.device)
        self.model.postprocess = False
        self.model.device = self.device
        self.model.eval()

    def generate_embedding(self, audio_path):
        return self.model(audio_path).to(self.device)

import os
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

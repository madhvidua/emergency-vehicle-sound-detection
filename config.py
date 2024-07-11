# config.py

import os

# Get the root project directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print(ROOT_DIR)

# Define other important directories
SRC_DIR = os.path.join(ROOT_DIR, 'src')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, 'embeddings')

# VGGish
MODEL_NAME = 'harritaylor/torchvggish'
MODEL_TYPE = 'vggish'

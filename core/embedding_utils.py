# core/embedding_utils.py

from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Load the pre-trained sentence transformer model
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts)

    def embed_query(self, query):
        # Encode query and ensure it's in the right format
        return np.array(self.model.encode([query])).astype("float32")

    def embed_chunks(self, chunks):
        # Encode all chunks and ensure they're in the right format
        return np.array(self.model.encode(chunks)).astype("float32")

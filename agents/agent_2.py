# agent_2.py
from mcp.message_protocol import MCPMessage

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class RetrievalAgent:
    def __init__(self, name="RetrievalAgent"):
        self.name = name
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.chunks = []

    def group_lines(self, lines, group_size=3):
        return [" ".join(lines[i:i+group_size]) for i in range(0, len(lines), group_size)]

    def embed_chunks(self, chunks):
        return self.model.encode(chunks).astype("float32")

    def build_index(self, text_path):
        with open(text_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        self.chunks = self.group_lines(lines)
        embeddings = self.embed_chunks(self.chunks)

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, query, k=10):
        query_embedding = self.model.encode([query]).astype("float32")
        D, I = self.index.search(query_embedding, k)
        return [self.chunks[i] for i in I[0] if i < len(self.chunks)]

    def handle_document(self, mcp_message):
        text_path = mcp_message.payload["text_path"]
        query = mcp_message.payload["query"]
        trace_id = mcp_message.trace_id

        self.build_index(text_path)
        results = self.retrieve(query)

        response = MCPMessage(
            sender=self.name,
            receiver="LLMResponseAgent",
            msg_type="RETRIEVAL_RESULT",
            trace_id=trace_id,
            payload={
                "retrieved_context": results,
                "query": query
            }
        )
        print(f"[{response.sender} ➜ {response.receiver}] {response.to_dict()}")  # 👈 log this
        return response
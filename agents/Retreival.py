#agents/retreival.py
# Import required modules for message passing and AI models
from mcp.message_protocol import MCPMessage
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class RetrievalAgent:
    def __init__(self, name="RetrievalAgent"):
        self.name = name  # Agent identifier
        # Load sentence transformer model for creating embeddings
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None  # FAISS search index
        self.chunks = []   # Store text chunks

    def group_lines(self, lines, group_size=3):
        return [" ".join(lines[i:i+group_size]) for i in range(0, len(lines), group_size)]

    def embed_chunks(self, chunks):
        return self.model.encode(chunks).astype("float32")

    def build_index(self, text_path):
        # Read and clean text lines
        with open(text_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Check if we have any text to process
        if not lines:
            print("⚠️ Warning: No text content found in document")
            self.chunks = []
            self.index = None
            return

        # Group lines into chunks and create embeddings
        self.chunks = self.group_lines(lines)
        
        # Check if we have chunks after grouping
        if not self.chunks:
            print("⚠️ Warning: No chunks created from text")
            self.index = None
            return
        
        embeddings = self.embed_chunks(self.chunks)
        
        # Verify embeddings were created successfully
        if embeddings.shape[0] == 0:
            print("⚠️ Warning: Failed to create embeddings")
            self.index = None
            return

        # Create FAISS index for fast similarity search
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, query, k=10):
        # Convert query to embedding
        query_embedding = self.model.encode([query]).astype("float32")
        # Search for similar chunks
        D, I = self.index.search(query_embedding, k)
        # Return the actual text chunks
        return [self.chunks[i] for i in I[0] if i < len(self.chunks)]

    def handle_document(self, mcp_message):
        # Extract information from message
        text_path = mcp_message.payload["text_path"]
        query = mcp_message.payload["query"]
        trace_id = mcp_message.trace_id

        # Build searchable index and retrieve relevant chunks
        self.build_index(text_path)
        results = self.retrieve(query)

        # Create response message for LLM agent
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
        print(f"[{response.sender} ➜ {response.receiver}] {response.to_dict()}")
        return response

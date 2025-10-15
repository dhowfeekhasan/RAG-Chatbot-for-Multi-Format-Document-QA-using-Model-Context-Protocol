# agents/ingestion.py
# Import required modules for message passing and document processing
from mcp.message_protocol import MCPMessage
from core.document_parser import process_file
import os

class IngestionAgent:
    def __init__(self, name="IngestionAgent"):
        self.name = name  # Agent identifier

    def handle_document(self, file_path, doc_type, trace_id):
        # Extract text and images from the document
        text_path, image_paths = process_file(file_path, doc_type)

        # Check if text extraction was successful
        if not text_path or not os.path.exists(text_path):
           raise FileNotFoundError(f"❌ Text extraction failed. File not found: {text_path}")

        # Return success message to next agent
        return MCPMessage(
            sender=self.name,
            receiver="RetrievalAgent",
            msg_type="DOCUMENT_CHUNKS",
            trace_id=trace_id,
            payload={
                "text_path": text_path,
                "image_paths": image_paths,
                "original_file": file_path,
                "status": "extraction_successful"
            }
        )

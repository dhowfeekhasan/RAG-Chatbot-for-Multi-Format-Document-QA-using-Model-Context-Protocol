# agents/agent_1.py

from mcp.message_protocol import MCPMessage
from core.document_parser import process_file
import os
class IngestionAgent:
    def __init__(self, name="IngestionAgent"):
        self.name = name

    def handle_document(self, file_path, doc_type, trace_id):
        text_path, image_paths = process_file(file_path, doc_type)

        if not text_path or not os.path.exists(text_path):
           raise FileNotFoundError(f"❌ Text extraction failed. File not found: {text_path}")

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

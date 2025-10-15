#agents/logging.py
# Import required modules for file operations and message passing
import os
import csv
from datetime import datetime
from mcp.message_protocol import MCPMessage

class LoggingAgent:
    def __init__(self, name="LoggingAgent"):
        self.name = name  # Agent identifier
        
        # Create logs directory in parent folder of agents/
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
        os.makedirs(self.log_dir, exist_ok=True)  # Create directory if it doesn't exist
        
        # Define the CSV log file path
        self.log_file = os.path.join(self.log_dir, "interaction_logs.csv")

    def handle_log(self, mcp_message):
        # Extract data from the message payload
        payload = mcp_message.payload
        trace_id = mcp_message.trace_id

        # Get all the information we want to log (with defaults)
        question = payload.get("query", "")           # User's question
        answer = payload.get("answer", "")            # Generated answer
        sources = payload.get("sources", [])          # Context chunks used
        file_name = payload.get("file_name", "")      # Original document name
        doc_type = payload.get("doc_type", "")        # Document type (pdf, docx, etc.)
        status = payload.get("status", "success")     # Success or error status
        error = payload.get("error", "")              # Error message if any

        # Create a preview of sources (first 80 chars of each chunk)
        # This helps us see what context was used without storing huge text blocks
        source_preview = " || ".join(chunk[:80].replace("\n", " ") for chunk in sources)

        # Create log entry as a list (CSV row)
        log_entry = [
            trace_id,                                    # Unique identifier for this interaction
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Timestamp
            file_name,                                   # Document filename
            question,                                    # User's question
            answer,                                      # Generated answer
            source_preview,                              # Preview of context used
            doc_type,                                    # Document type
            status,                                      # Success/error status
            error                                        # Error details if any
        ]

        # Check if log file exists (to decide if we need headers)
        file_exists = os.path.isfile(self.log_file)
        
        # Write to CSV file
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # If file is new, write headers first
            if not file_exists:
                writer.writerow([
                    "trace_id", "timestamp", "filename", "question", "answer",
                    "sources", "document_type", "status", "error_message"
                ])
            
            # Write the actual log entry
            writer.writerow(log_entry)

        # Return confirmation message
        return MCPMessage(
            sender=self.name,
            receiver="System",
            msg_type="LOGGING_DONE",
            trace_id=trace_id,
            payload={"status": "logged"}
        )

import os
import csv
from datetime import datetime
from mcp.message_protocol import MCPMessage

class LoggingAgent:
    def __init__(self, name="LoggingAgent"):
        self.name = name
        self.log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "interaction_logs.csv")

    def handle_log(self, mcp_message):
        payload = mcp_message.payload
        trace_id = mcp_message.trace_id

        question = payload.get("query", "")
        answer = payload.get("answer", "")
        sources = payload.get("sources", [])
        file_name = payload.get("file_name", "")
        doc_type = payload.get("doc_type", "")
        status = payload.get("status", "success")
        error = payload.get("error", "")

        source_preview = " || ".join(chunk[:80].replace("\n", " ") for chunk in sources)

        log_entry = [
            trace_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_name,
            question,
            answer,
            source_preview,
            doc_type,
            status,
            error
        ]

        file_exists = os.path.isfile(self.log_file)
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "trace_id", "timestamp", "filename", "question", "answer",
                    "sources", "document_type", "status", "error_message"
                ])
            writer.writerow(log_entry)

        return MCPMessage(
            sender=self.name,
            receiver="System",
            msg_type="LOGGING_DONE",
            trace_id=trace_id,
            payload={"status": "logged"}
        )

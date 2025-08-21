import os
import uuid
from agents.Ingestion import IngestionAgent
from agents.Retreival import RetrievalAgent
from agents.llm import LLMResponseAgent
from agents.logging import LoggingAgent 
from mcp.message_protocol import MCPMessage

class Coordinator:
    def __init__(self):
        self.ingestion_agent = IngestionAgent()
        self.retrieval_agent = RetrievalAgent()
        self.llm_response_agent = LLMResponseAgent()
        self.logging_agent = LoggingAgent()

    def handle_user_query(self, file_path, document_type, user_question, trace_id):
        ingestion_msg = MCPMessage(
            sender="UI",
            receiver="IngestionAgent",
            msg_type="DOCUMENT_UPLOAD",
            trace_id=trace_id,
            payload={
                "file_path": file_path,
                "document_type": document_type
            }
        )
        print(f"[{ingestion_msg.sender} ➜ {ingestion_msg.receiver}] {ingestion_msg.to_dict()}")

        ingestion_response = self.ingestion_agent.handle_document(file_path, document_type, trace_id)

        retrieval_msg = MCPMessage(
            sender="IngestionAgent",
            receiver="RetrievalAgent",
            msg_type="DOCUMENT_CHUNKS",
            trace_id=trace_id,
            payload={
                "text_path": ingestion_response.payload["text_path"],
                "query": user_question
            }
        )
        print(f"[{retrieval_msg.sender} ➜ {retrieval_msg.receiver}] {retrieval_msg.to_dict()}")

        retrieval_response = self.retrieval_agent.handle_document(retrieval_msg)

        llm_response = self.llm_response_agent.handle_context(retrieval_response)

        # Log the interaction
        log_msg = MCPMessage(
            sender="Coordinator",
            receiver="LoggingAgent",
            msg_type="LOGGING_REQUEST",
            trace_id=trace_id,
            payload={
                "query": user_question,
                "answer": llm_response.payload["answer"],
                "sources": llm_response.payload["sources"],
                "file_name": os.path.basename(file_path),
                "doc_type": document_type,
                "status": "success",
                "error": ""
            }
        )
        self.logging_agent.handle_log(log_msg)

        return llm_response


if __name__ == "__main__":
    coordinator = Coordinator()
    uploaded_file = None
    doc_ext = None
    trace_id_counter = 1

    print("\n🤖 Agentic RAG Chatbot for Multi-Format Document QA (MCP)\n")

    while True:
        print("\nSelect an option:")
        print("1. Upload new document")
        print("2. Ask a question")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            file_path = input("📂 Enter the path to your document: ").strip()
            if not os.path.isfile(file_path):
                print("❌ File not found. Please check the path.")
                continue

            ext = os.path.splitext(file_path)[-1].lower().replace(".", "")
            supported_types = ["pdf", "docx", "pptx", "csv", "xlsx", "txt", "png", "jpg", "jpeg"]

            if ext not in supported_types:
                print(f"❌ Unsupported file type: .{ext}")
                continue

            uploaded_file = file_path
            doc_ext = ext
            print("✅ File uploaded successfully.")

        elif choice == "2":
            if not uploaded_file:
                print("⚠️ Please upload a document first.")
                continue

            question = input("❓ Enter your question about the document: ").strip()
            trace_id = f"trace-{trace_id_counter:03}"
            trace_id_counter += 1

            result = coordinator.handle_user_query(uploaded_file, doc_ext, question, trace_id)

            print("\n✅ Final Answer:")
            print(result.payload["answer"])

        elif choice == "3":
            print("👋 Exiting. Have a nice day!")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

#main/coordinator.py
import os
import sys
import uuid
import time 

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.Ingestion import IngestionAgent
from agents.Retreival import RetrievalAgent
from agents.llm import LLMResponseAgent
from agents.logging import LoggingAgent 
from mcp.message_protocol import MCPMessage

class Coordinator:
    """
    Central coordinator that manages all agents and orchestrates the RAG pipeline
    Think of this as the "conductor" of an orchestra - it tells each agent when to play their part
    """
    
    def __init__(self):
        """Initialize all agents that will work together"""
        self.ingestion_agent = IngestionAgent()      # Processes documents
        self.retrieval_agent = RetrievalAgent()      # Finds relevant text chunks
        self.llm_response_agent = LLMResponseAgent() # Generates answers
        self.logging_agent = LoggingAgent()          # Records everything

    def handle_user_query(self, file_path, document_type, user_question, trace_id):
        """
        Main pipeline that processes user queries through all agents
        Args:
            file_path: Path to the uploaded document
            document_type: Type of document (pdf, docx, etc.)
            user_question: The question user wants answered
            trace_id: Unique identifier to track this request
        Returns:
            Tuple: (final_response_message, performance_metrics)
        """
        
        # Start total time measurement
        total_start_time = time.time()
        performance_metrics = {}
        
        # STEP 1: Send document to Ingestion Agent for processing
        print("\n" + "="*60)
        print("⏱️  PERFORMANCE TRACKING")
        print("="*60)
        
        # Create message for document upload
        ingestion_msg = MCPMessage(
            sender="UI",                        # Message comes from user interface
            receiver="IngestionAgent",          # Send to ingestion agent
            msg_type="DOCUMENT_UPLOAD",         # Type of request
            trace_id=trace_id,                  # For tracking
            payload={
                "file_path": file_path,
                "document_type": document_type
            }
        )
        print(f"\n[{ingestion_msg.sender} ➜ {ingestion_msg.receiver}] {ingestion_msg.to_dict()}")

        # Measure ingestion time
        ingestion_start = time.time()
        ingestion_response = self.ingestion_agent.handle_document(file_path, document_type, trace_id)
        ingestion_time = time.time() - ingestion_start
        performance_metrics['ingestion_time'] = ingestion_time
        print(f"✅ Ingestion completed in {ingestion_time:.3f}s")

        # STEP 2: Send extracted text to Retrieval Agent for indexing and searching
        # Create message for retrieval
        retrieval_msg = MCPMessage(
            sender="IngestionAgent",            # Message comes from ingestion
            receiver="RetrievalAgent",          # Send to retrieval agent
            msg_type="DOCUMENT_CHUNKS",         # Type of request
            trace_id=trace_id,                  # For tracking
            payload={
                "text_path": ingestion_response.payload["text_path"],  # Where text was saved
                "query": user_question          # User's question to search for
            }
        )
        print(f"\n[{retrieval_msg.sender} ➜ {retrieval_msg.receiver}] {retrieval_msg.to_dict()}")

        # Measure retrieval time
        retrieval_start = time.time()
        retrieval_response = self.retrieval_agent.handle_document(retrieval_msg)
        retrieval_time = time.time() - retrieval_start
        performance_metrics['retrieval_time'] = retrieval_time
        print(f"✅ Retrieval completed in {retrieval_time:.3f}s")

        # STEP 3: Send query and context to LLM Agent for answer generation
        llm_start = time.time()
        llm_response = self.llm_response_agent.handle_context(retrieval_response)
        llm_time = time.time() - llm_start
        performance_metrics['llm_time'] = llm_time
        print(f"✅ LLM response generated in {llm_time:.3f}s")

        # STEP 4: Log the entire interaction for analysis and debugging
        logging_start = time.time()
        log_msg = MCPMessage(
            sender="Coordinator",               # Message comes from coordinator
            receiver="LoggingAgent",            # Send to logging agent
            msg_type="LOGGING_REQUEST",         # Type of request
            trace_id=trace_id,                  # For tracking
            payload={
                "query": user_question,                                    # User's question
                "answer": llm_response.payload["answer"],                  # Generated answer
                "sources": llm_response.payload["sources"],               # Context chunks used
                "file_name": os.path.basename(file_path),                 # Just filename, not full path
                "doc_type": document_type,                                 # Document type
                "status": "success",                                       # Success indicator
                "error": ""                                                # No error message
            }
        )
        self.logging_agent.handle_log(log_msg)
        logging_time = time.time() - logging_start
        performance_metrics['logging_time'] = logging_time
        print(f"✅ Logging completed in {logging_time:.3f}s")

        # Calculate total time
        total_time = time.time() - total_start_time
        performance_metrics['total_time'] = total_time
        
        # Print performance summary
        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)
        print(f"📄 Ingestion:  {ingestion_time:.3f}s ({(ingestion_time/total_time)*100:.1f}%)")
        print(f"🔍 Retrieval:  {retrieval_time:.3f}s ({(retrieval_time/total_time)*100:.1f}%)")
        print(f"🤖 LLM:        {llm_time:.3f}s ({(llm_time/total_time)*100:.1f}%)")
        print(f"📝 Logging:    {logging_time:.3f}s ({(logging_time/total_time)*100:.1f}%)")
        print(f"⏱️  TOTAL:      {total_time:.3f}s")
        print("="*60 + "\n")

        return llm_response, performance_metrics


# Command line interface - only runs if this file is executed directly
if __name__ == "__main__":
    # Initialize the coordinator
    coordinator = Coordinator()
    uploaded_file = None      # Track currently uploaded file
    doc_ext = None           # Track document extension
    trace_id_counter = 1     # Counter for generating unique trace IDs

    print("\n🤖 Agentic RAG Chatbot for Multi-Format Document QA (MCP)\n")

    # Main interaction loop
    while True:
        print("\nSelect an option:")
        print("1. Upload new document")
        print("2. Ask a question")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            # Handle document upload
            file_path = input("📂 Enter the path to your document: ").strip()
            
            # Check if file exists
            if not os.path.isfile(file_path):
                print("❌ File not found. Please check the path.")
                continue

            # Extract file extension and validate
            ext = os.path.splitext(file_path)[-1].lower().replace(".", "")
            supported_types = ["pdf", "docx", "pptx", "csv", "xlsx", "txt", "png", "jpg", "jpeg"]

            if ext not in supported_types:
                print(f"❌ Unsupported file type: .{ext}")
                continue

            # Store file info for later use
            uploaded_file = file_path
            doc_ext = ext
            print("✅ File uploaded successfully.")

        elif choice == "2":
            # Handle question asking
            if not uploaded_file:
                print("⚠️ Please upload a document first.")
                continue

            # Get user's question
            question = input("❓ Enter your question about the document: ").strip()
            
            # Generate unique trace ID for this interaction
            trace_id = f"trace-{trace_id_counter:03}"
            trace_id_counter += 1

            # Process the query through the entire pipeline with performance tracking
            result, metrics = coordinator.handle_user_query(uploaded_file, doc_ext, question, trace_id)

            # Display the final answer
            print("\n✅ Final Answer:")
            print(result.payload["answer"])

        elif choice == "3":
            # Exit the program
            print("👋 Exiting. Have a nice day!")
            break
        else:
            # Invalid choice
            print("❌ Invalid choice. Please select 1, 2, or 3.")

# 🤖 RAG Chatbot for Multi-Format Document QA using Model Context Protocol (MCP) 
By Dhowfeek Hasan 

An **Agent-Based** chatbot system capable of answering user queries over **multi-format documents** (PDF, DOCX, PPTX, TXT, CSV, XLSX, Images) using **Retrieval-Augmented Generation (RAG)** and **Model Context Protocol (MCP)**.

<img width="1914" height="843" alt="image" src="https://github.com/user-attachments/assets/ead6968d-9c77-4b3e-8e4e-5cc54b301faa" />



---

## 📌 Features

- Agent-based modular architecture (Ingestion, Retrieval, LLM Response)
-  Multi-format document support
- Intelligent retrieval with vector embeddings
- Streamlit-based chatbot UI
- Continuous query loop with trace logging
- Automatic logging of interactions (`logs/interaction_log.csv`)
- LLM support

---
## 📌 System Flow Diagram 
![image](https://github.com/user-attachments/assets/6dea681e-3e44-4ca0-aa5b-30602db26d58)


## 💻 Run the Application
Step 1 :  Create Virtual Environment
-      python -m venv venv
-      venv\Scripts\activate
  
Step 2 : Install dependencies
-      pip install --upgrade pip
-      pip install -r requirements.txt
           
Step 3 : To run UI    
  -      streamlit run ui/app.py   # Streamlit UI 
-        python main/coordinator.py   #Command-line Interface


## 🧱 Project Structure 

     ├── agents/ # Agent1: Ingestion, Agent2: Retrieval, Agent3: LLM Response
     ├── core/ # Text extraction & embedding utils
     ├── main/ # Coordinator orchestrating agents
     ├── mcp/ # Message protocol definition
     ├── ui/ # Streamlit chat UI
     ├── extracted_data/ # Temporary text extracted from files
     ├── uploaded_docs/ # Uploaded input documents
     ├── logs/ # Auto-generated interaction logs
     └── requirements.txt

👨‍💻 Developer
Developed by Dhowfeek Hasan

📝 License
This project is for educational and demonstration purposes. Reach out if you plan to use commercially.




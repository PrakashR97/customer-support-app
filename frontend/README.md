# CrewAI Customer Support Agent

A customer support system built using **CrewAI**, **RAG (Retrieval-Augmented Generation)**, **FAISS**, **OpenAI Embeddings**, and **Web Search**.

The system uses a three-agent workflow:

1. **Tier 1 PDF Support Agent** – Searches the company policy PDF using RAG.
2. **Tier 2 Web Researcher** – Searches the web when the PDF does not contain the answer.
3. **System Auditor** – Logs the customer question and final answer into a text file.

---

## Architecture

```text
                    Customer Question
                           |
                           v
                  +-------------------+
                  |   Agent 1         |
                  | PDF Support Agent |
                  +-------------------+
                           |
                    Search PDF using
                    RAG + FAISS
                           |
              +------------+------------+
              |                         |
        Answer Found              Answer Not Found
              |                         |
              |                         v
              |                  FALLBACK_REQUIRED
              |                         |
              |                         v
              |                  +--------------+
              |                  |   Agent 2    |
              |                  | Web Research |
              |                  +--------------+
              |                         |
              |                    Web Search
              |                         |
              +------------+------------+
                           |
                           v
                    Final Answer
                           |
                           v
                  +----------------+
                  |    Agent 3     |
                  | System Auditor |
                  +----------------+
                           |
                           v
                  conversation.txt
```

---

# Features

* CrewAI multi-agent workflow
* PDF-based RAG
* FAISS vector database
* OpenAI `text-embedding-3-small`
* Semantic similarity search
* Web fallback using Serper
* Conversation logging
* Sequential agent execution
* Environment variable support using `.env`

---

# Project Structure

```text
crewai-customer-support/
│
├── main.py
├── company_policy.pdf
├── conversation.txt
├── .env
├── .gitignore
└── requirements.txt
```

---

# How It Works

## Agent 1 – Tier 1 PDF Support

The first agent is responsible for answering questions using the company policy PDF.

The PDF is loaded using:

```python
loader = PyPDFLoader("company_policy.pdf")
pages = loader.load()
```

The PDF content is then split into smaller chunks:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30
)
```

The chunks are converted into embeddings using:

```python
OpenAIEmbeddings(model="text-embedding-3-small")
```

The embeddings are stored in a FAISS vector store:

```python
vector_store = FAISS.from_documents(
    chunks,
    embedding_model
)
```

When the customer asks a question, the system searches the vector store:

```python
matches = vector_store.similarity_search(query, k=2)
```

The two most relevant chunks are returned to the agent.

---

# RAG Flow

The RAG process works like this:

```text
PDF
 |
 v
Load PDF
 |
 v
Split into Chunks
 |
 v
Generate Embeddings
 |
 v
FAISS Vector Store
 |
 v
Customer Question
 |
 v
Similarity Search
 |
 v
Relevant PDF Chunks
 |
 v
CrewAI Agent
 |
 v
Answer
```

---

# Agent 2 – Web Researcher

If Agent 1 cannot find the answer in the company PDF, it returns:

```text
FALLBACK_REQUIRED for [Company Name]
```

Agent 2 then detects this response.

For example:

```text
Customer Question:
Who is the CEO?

Agent 1:
FALLBACK_REQUIRED for Apple Inc.
```

Agent 2 creates a web search query such as:

```text
Apple Inc. Who is the CEO?
```

The web search is performed using:

```python
web_search_tool = SerperDevTool()
```

This allows the system to retrieve information that is not available in the internal company document.

---

# Agent 3 – System Auditor

The third agent is responsible for logging the interaction.

It uses a custom CrewAI tool:

```python
@tool("File Writer Tool")
def file_writer_tool(log_content: str) -> str:
```

The tool writes the conversation to:

```text
conversation.txt
```

The log format is:

```text
----------------------------------------
Timestamp: 2026-10-08 20:00:00
User Question: Who is the CEO?
Final Answer: ...
----------------------------------------
```

Each new interaction is appended to the existing file.

---

# Technologies Used

| Technology        | Purpose                                    |
| ----------------- | ------------------------------------------ |
| Python            | Application development                    |
| CrewAI            | Multi-agent orchestration                  |
| LangChain         | PDF loading, text splitting and embeddings |
| PyPDFLoader       | PDF document loading                       |
| OpenAI Embeddings | Convert text into vectors                  |
| FAISS             | Vector similarity search                   |
| Serper            | Web search                                 |
| dotenv            | Environment variable management            |

---

# Installation

## 1. Create a Virtual Environment

Use Python 3.12.

```bash
python3.12 -m venv venv12
```

Activate the environment:

### macOS / Linux

```bash
source venv12/bin/activate
```

You should see:

```text
(venv12)
```

---

# 2. Install Dependencies

Create a `requirements.txt` file containing:

```text
crewai
crewai-tools
langchain-community
langchain-text-splitters
langchain-openai
faiss-cpu
pypdf
python-dotenv
```

Install them:

```bash
pip install -r requirements.txt
```

---

# 3. Configure API Keys

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

Do not commit `.env` to GitHub.

Add it to `.gitignore`:

```text
.env
venv12/
__pycache__/
conversation.txt
```

---

# 4. Add the Company PDF

Place your company policy document in the project directory:

```text
company_policy.pdf
```

The application expects this exact filename:

```python
loader = PyPDFLoader("company_policy.pdf")
```

If your PDF has a different name, update the code accordingly.

---

# Running the Application

Run:

```bash
python main.py
```

You will see:

```text
--- Welcome to the Support System ---

Please enter your question:
```

Enter your question.

For example:

```text
What is the company's leave policy?
```

The CrewAI workflow will execute:

```text
Customer Question
       |
       v
Agent 1 - Search PDF
       |
       v
Answer Found?
   /          \
 Yes           No
 |              |
 v              v
Answer      Agent 2
             Web Search
                |
                v
          Final Answer
                |
                v
             Agent 3
                |
                v
       conversation.txt
```

---

# Example 1 – Answer Found in PDF

User:

```text
What is the company's work-from-home policy?
```

Agent 1 searches the PDF.

If the policy exists in the PDF:

```text
Agent 1
   |
   v
Relevant PDF Content
   |
   v
Policy Answer
```

Agent 2 receives the answer from Agent 1 and returns the answer.

Agent 3 logs the interaction.

---

# Example 2 – Answer Not Found in PDF

User:

```text
Who is the CEO of the company?
```

If the PDF does not contain the answer, Agent 1 returns something similar to:

```text
FALLBACK_REQUIRED for Apple Inc.
```

Agent 2 then searches the web:

```text
Apple Inc. Who is the CEO?
```

The final answer is returned to the customer.

Agent 3 saves the interaction.

---

# Important CrewAI Concepts Demonstrated

## 1. Agents

The project contains three agents:

```python
agent_1_rag
agent_2_web
agent_3_logger
```

Each agent has a specific responsibility.

---

## 2. Tasks

There are three tasks:

```python
task_1
task_2
task_3
```

The tasks are executed sequentially.

---

## 3. Process

The Crew uses:

```python
process=Process.sequential
```

This means:

```text
Task 1
  ↓
Task 2
  ↓
Task 3
```

Task 2 receives Task 1's output through:

```python
context=[task_1]
```

---

# Custom CrewAI Tool

The project also demonstrates how to create a custom CrewAI tool.

```python
@tool("File Writer Tool")
def file_writer_tool(log_content: str) -> str:
```

The tool allows an agent to write information to a local file.

This demonstrates that CrewAI agents can use custom Python functions as tools.

---

# RAG vs Web Search

The application uses two different knowledge sources.

### Internal Knowledge

```text
company_policy.pdf
       ↓
RAG
       ↓
FAISS
       ↓
Agent 1
```

### External Knowledge

```text
Internet
   ↓
Serper
   ↓
Agent 2
```

This creates a useful fallback architecture:

```text
Internal Knowledge First
        ↓
External Knowledge Second
```

---

# Environment Variables

The application uses:

```python
load_dotenv()
```

This loads API keys from `.env`.

Example:

```text
OPENAI_API_KEY=xxxxx
SERPER_API_KEY=xxxxx
```

Never hard-code API keys directly in Python code.

---

# Conversation Logging

Every interaction is stored in:

```text
conversation.txt
```

The file is opened using append mode:

```python
open("conversation.txt", "a", encoding="utf-8")
```

The `"a"` mode means:

* Create the file if it does not exist.
* Add new logs to the end of the file.
* Preserve previous conversations.

---

# Future Improvements

The current implementation can be extended with:

### 1. React Frontend

Replace the command-line interface:

```python
input("Please enter your question: ")
```

with a React frontend.

Architecture:

```text
React
  |
  | HTTP API
  v
FastAPI
  |
  v
CrewAI
  |
  +---- RAG / FAISS
  |
  +---- Web Search
  |
  +---- File Logging
```

### 2. FastAPI Backend

Expose the CrewAI workflow through an API endpoint.

Example:

```text
POST /ask
```

Request:

```json
{
    "question": "What is the leave policy?"
}
```

Response:

```json
{
    "answer": "..."
}
```

### 3. Streaming Responses

The backend can stream CrewAI responses to the React frontend.

### 4. Persistent Vector Database

Instead of creating the FAISS database every time the application starts, the vector store can be saved and loaded.

### 5. Multiple PDFs

The application can be extended to support:

```text
company_policy.pdf
employee_handbook.pdf
benefits.pdf
security_policy.pdf
```

### 6. Conversation Memory

Conversation history can be added so the support agent can understand follow-up questions.

### 7. Authentication

A login system can be added when the application is exposed to real users.

---

# Summary

This project demonstrates a **three-agent customer support architecture using CrewAI**.

```text
                Customer
                   |
                   v
             Tier 1 Agent
                   |
             PDF / RAG Search
                   |
          +--------+--------+
          |                 |
       Found            Not Found
          |                 |
          |                 v
          |            Web Agent
          |                 |
          |            Web Search
          |                 |
          +--------+--------+
                   |
                   v
              Final Answer
                   |
                   v
             Logger Agent
                   |
                   v
          conversation.txt
```

The main concepts demonstrated are:

* CrewAI Agents
* CrewAI Tasks
* Sequential Process
* Task Context
* Custom Tools
* RAG
* FAISS
* OpenAI Embeddings
* PDF Search
* Web Search
* Fallback Architecture
* Conversation Logging
* Environment Variables

import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Your existing CrewAI imports ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from crewai_tools import SerperDevTool

load_dotenv()

# 1. Initialize FastAPI & CORS (Allows React to talk to Python)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # React/Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup Vector Store (Runs once when server starts)
loader = PyPDFLoader("company_policy.pdf")
pages = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
chunks = text_splitter.split_documents(pages)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_documents(chunks, embedding_model)

# 3. Define Tools
@tool("PDF Search Tool")
def pdf_search_tool(query: str) -> str:
    """Searches the official company PDF for policies."""
    matches = vector_store.similarity_search(query, k=2)
    return "\n\n".join([doc.page_content for doc in matches])

web_search_tool = SerperDevTool()

@tool("File Writer Tool")
def file_writer_tool(log_content: str) -> str:
    """Appends the formatted conversation log to a text file."""
    with open("conversation.txt", "a", encoding="utf-8") as file:
        file.write(log_content + "\n\n")
    return "Successfully written to conversation.txt"


# 4. Define Agents
agent_1_rag = Agent(
    role="Tier 1 PDF Support",
    goal="Answer questions strictly using the PDF Search Tool.",
    backstory="You search the company PDF for answers. If the PDF does not answer the question, "
              "identify the company name mentioned in the PDF (e.g., 'Apple Inc.') and output "
              "EXACTLY: 'FALLBACK_REQUIRED for [Company Name]'. Do not guess the answer.",
    verbose=True,
    allow_delegation=False,
    tools=[pdf_search_tool]
)

agent_2_web = Agent(
    role="Tier 2 Web Researcher",
    goal="Find answers online when Tier 1 cannot find them in internal documents.",
    backstory="You check Tier 1's response. If Tier 1 provided an answer, return it directly. "
              "If Tier 1 outputs 'FALLBACK_REQUIRED for [Company Name]', formulate a specific web search query "
              "combining the company name and the customer's question (e.g., 'CEO of Apple Inc.') using the web_search_tool.",
    verbose=True,
    allow_delegation=False,
    tools=[web_search_tool]
)

agent_3_logger = Agent(
    role="System Auditor",
    goal="Format and save the conversation history accurately.",
    backstory="You observe the question and the final answer. You use the File Writer Tool to save a clean log.",
    verbose=True,
    allow_delegation=False,
    tools=[file_writer_tool]
)

# 5. Define Tasks
task_1 = Task(
    description="Customer Question: '{customer_question}'. "
                "1. Search the PDF to answer the question. "
                "2. If the answer is NOT in the PDF, find the company name in the document and output "
                "'FALLBACK_REQUIRED for [Company Name]'.",
    expected_output="The policy answer from the PDF, or 'FALLBACK_REQUIRED for [Company Name]'.",
    agent=agent_1_rag
)

task_2 = Task(
    description="Customer Question: '{customer_question}'. "
                "Look at Task 1's output. "
                "- If Task 1 provided a valid answer from the PDF, output that answer. "
                "- If Task 1 output contains 'FALLBACK_REQUIRED for [Company Name]', extract the company name and "
                "use the web search tool to search: '[Company Name] {customer_question}'. "
                "Then provide the final clear answer.",
    expected_output="The final direct answer to the customer's question.",
    agent=agent_2_web,
    context=[task_1]
)

task_3 = Task(
    description="""
    Create a log entry for this interaction. 
    Customer Question: '{customer_question}'
    Final Answer: Get this from Task 2's output.
    
    Format it EXACTLY like this:
    ----------------------------------------
    Timestamp: {current_time}
    User Question: [Insert Question]
    Final Answer: [Insert Final Answer]
    ----------------------------------------
    
    Use the File Writer Tool to save this formatted text.
    """,
    expected_output="A confirmation that the file was written.",
    agent=agent_3_logger
)
class UserQuery(BaseModel):
    question: str



@app.post("/api/ask")
async def ask_support(query: UserQuery):
    crew = Crew(
        agents=[agent_1_rag, agent_2_web, agent_3_logger],
        tasks=[task_1, task_2, task_3],
        process=Process.sequential
    )

    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Kickoff the crew asynchronously
    result = await crew.kickoff_async(inputs={
        "customer_question": query.question,
        "current_time": current_timestamp
    })

    # Return the final output to React
    return {"answer": str(result)}
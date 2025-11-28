import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore
from ddgs import DDGS
from dataclasses import dataclass
from typing_extensions import TypedDict

db_name = "vector_db"
db_abs_path = os.path.abspath(db_name)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")

store = InMemoryStore()

@dataclass
class Context:
    user_id: str

@tool
def get_histories(runtime: ToolRuntime[Context]):
    """
    Retrieve conversation history from memory store.
    Use this tool at the START of conversation to check past context and user preferences.
    
    **IMPORTANT:** Always call this tool first when user asks:
    - Questions about their previous messages
    - "Do you remember...?"
    - "What did I say about...?"
    - Or when you need context from past conversations
    
    Returns:
        String containing past conversation messages (last 10 messages)
    """
    user_store = runtime.store
    user_id = runtime.context.user_id
    
    try:
        store_data = user_store.get(("conversations",), user_id)
        if store_data:
            messages = store_data.value.get("messages", [])
            if messages:
                formatted = []
                for i, msg in enumerate(messages, 1):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    formatted.append(f"{i}. {role}: {content}")
                return "Past conversation:\n" + "\n".join(formatted)
        return "No conversation history found."
    except Exception as e:
        return f"Error retrieving history: {e}"   
        
@tool
def save_context(message: str, role: str, runtime: ToolRuntime[Context]) -> str:
    """
    Save conversation messages to memory store.
    This tool automatically saves important context from conversations.
    
    Use this ONLY when:
    - User shares important information (name, preferences, facts)
    - You want to remember specific context for future reference
    
    DO NOT use for every single message - only important ones.
    
    Args:
        message: The message content to save
        role: Either "human" or "assistant"
        runtime: Tool runtime context with store and user_id
    
    Returns:
        Success message confirming conversation was saved
    """
    user_store = runtime.store
    user_id = runtime.context.user_id
    
    try:
        existing = user_store.get(("conversations",), user_id)
        messages = existing.value.get("messages", []) if existing else []
    except:
        messages = []
    
    # Append new message
    messages.append({"role": role, "content": message})
    
    # Save back
    user_store.put(("conversations",), user_id, {"messages": messages})
    
    return f"Successfully saved {role} message to conversation history."

@tool
def web_search(query: str, num_results: int=10) -> str:
    """
    Search the web using DuckDuckGo for CURRENT or RECENT information only.
    DO NOT use this tool for greetings, general knowledge, or simple questions.

    Args:
        query: search query string
        num_results: Number of results to return (default: 10)
    
    Returns:
        formatted search results with titles, descriptions, and URLs
    """
    try:
        # Handle empty string or invalid num_results
        if isinstance(num_results, str):
            num_results = int(num_results) if num_results else 10
        
        results = list(DDGS().text(
            query=query,
            max_results=num_results,
            region="id-en",
            timelimit="d",
            backend="google, bing, brave, yahoo, wikipedia, duckduckgo"
        ))
        if not results:
            return f"No results found for {query}"
        formatted_results = [f"Search results for '{query}':\n"]
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            body = result.get("body", "No description available")
            href = result.get("href", "")
            formatted_results.append(f"{i}. **{title}**\n {body}\n {href}")
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def retrieve_context(query: str, k: int=5)-> str:
    """
    Retrieve relevant information from UPLOADED DOCUMENTS only.
    DO NOT use this tool for greetings, general knowledge, or when no document is uploaded.

    Args:
        query: The query to search for in the document.
        k: The number of relevant documents to return.
    Returns:
        A string containing the relevant information from the document.
        If the vector store is not found, answer the user directly without tools.
    """
    try:
        vector_store = FAISS.load_local(
            db_name,
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        return "Vector store not found. Please upload a document first."
    
    docs = vector_store.similarity_search(query=query, k=k)
    context = "\n\n".join(f"{i+1}. Source: {doc.metadata.get('source', '-')} (Page: {doc.metadata.get('page', '-')})\n {doc.page_content}" for i, doc in enumerate (docs))
    return context

tools = [
    get_histories,
    retrieve_context,
    web_search,
    save_context
]
import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool
from ddgs import DDGS


db_name = "vector_db"
db_abs_path = os.path.abspath(db_name)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")

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

def do_nothing(query: str) -> str:
    """
    This tool does nothing and is used to handle cases where no tool is needed.
    It is a placeholder to ensure the agent can respond without using tools.
    """
    return "No action taken. You can ask me anything else or use a tool if needed."

tools = [
    retrieve_context,
    web_search,
    do_nothing,
]
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import AIMessage
from .tools import tools

class Assistant:
    def __init__(self, base_url="http://localhost:11434", llm_model="llama3.2:3b"):
        self.llm = ChatOllama(model=llm_model, base_url=base_url)
        
        system_prompt = """
        You are a helpful AI assistant. You can answer questions directly or use tools when necessary.
        
        **CRITICAL RULES:**
        ⚠️ DO NOT use tools for: greetings (hi, hello, hey), simple conversations, general knowledge, math, or definitions
        ✅ Answer these questions DIRECTLY without any tools
        
        **Available Tools (use ONLY when necessary):**
        - retrieve_context: ONLY for questions about uploaded documents
        - web_search: ONLY for current news, recent events, or real-time information
        - do_nothing: Use when no other tool is needed
        
        **When to use tools:**
        - retrieve_context: User asks "summarize the document", "what does the document say about X"
        - web_search: User asks "latest news", "current events", "what happened today"
        - do_nothing: Use when no other tool is needed
        
        **When NOT to use tools:**
        - Greetings: "hello", "hi", "hey" → Just greet back
        - General knowledge: "what is Python?", "explain AI" → Answer directly
        - Math: "what's 2+2?" → Answer directly
        - Simple questions: "how are you?", "what can you do?" → Answer directly
        
        Be friendly, concise, and helpful. Use markdown for formatting.
        """
        self.agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=system_prompt
        )


        
    def chat(self, session_id, question):
        for event in self.agent.stream({"messages": [{"role":"human", "content":question}]}, stream_mode="values"):
            msg = event["messages"][-1]
            print(f"Message: {msg}\n")
            if isinstance(msg, AIMessage) and msg.content:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    continue 
                yield msg.content
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import AIMessage
import re

from .tools import tools
from .tools import store, Context

class Assistant:
    def __init__(self, base_url="http://localhost:11434", llm_model="llama3.2:3b"):
        self.llm = ChatOllama(model=llm_model, base_url=base_url)
        
        system_prompt = """
        You are a helpful AI assistant with memory capabilities. You MUST follow this workflow for EVERY conversation:

        **MANDATORY WORKFLOW FOR EVERY MESSAGE:**
        1. **ALWAYS start by calling get_histories** to check past conversations and user preferences
        2. **Answer the user's question** based on history context and current query
        3. **ALWAYS end by calling save_context** to save both user message and your response

        **CRITICAL RULES:**
        **ALWAYS use get_histories FIRST** - even for simple greetings
        **ALWAYS use save_context LAST** - to remember the conversation
        For document questions → Also use retrieve_context
        For current events → Also use web_search

        **Available Tools (use in this order):**
        1. **get_histories** - MANDATORY first step for every message
        2. **retrieve_context** - Use when user asks about uploaded documents
        3. **web_search** - Use when user asks about current news/events
        4. **save_context** - MANDATORY last step for every message

        **When to use additional tools:**
        - retrieve_context: "summarize the document", "what does the document say about X"
        - web_search: "latest news", "current events", "what happened today"

        **Example workflow:**
        User: "hello"
        1. Call get_histories() → Check past conversations
        2. Respond: "Hello! Based on our history..." 
        3. Call save_context(message="hello", role="human") → Save user message
        4. Call save_context(message="Hello! Based on...", role="assistant") → Save your response

        User: "my name is John"
        1. Call get_histories() → Check past conversations
        2. Respond: "Nice to meet you John! I'll remember that."
        3. Call save_context(message="my name is John", role="human") → Save user message
        4. Call save_context(message="Nice to meet you John...", role="assistant") → Save your response

        **REMEMBER:** 
        - get_histories = FIRST tool for every message
        - save_context = LAST tool for every message (save both user and assistant messages)
        - Be friendly, concise, and helpful
        - Use markdown formatting
        """
        
        self.agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=system_prompt,
            store=store,
            context_schema=Context,
        )

    def _post_process(self, msg):
        cleaned_content = re.sub(r'<think>.*?</think>', '', msg.content, flags=re.DOTALL)
        cleaned_content = cleaned_content.strip()
        return cleaned_content
       

    def chat(self, session_id, question):
        for event in self.agent.stream(
            {"messages": [{"role": "human", "content": question}]}, 
            stream_mode="values", 
            context=Context(user_id=session_id)
            ):
            msg = event["messages"][-1]
            print(f"Message: {msg}\n")
            if isinstance(msg, AIMessage) and msg.content:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    continue 
                cleaned_content = self._post_process(msg)
                if cleaned_content:
                    yield cleaned_content
from langchain_ollama import ChatOllama
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///chat_history.db")

base_url = "http://localhost:11434"
model = "llama3.2:3b"
llm = ChatOllama(base_url=base_url, model=model)


system_with_context = SystemMessagePromptTemplate.from_template(
    "You are a helpful AI assistant who answers user questions based on the provided context."
)

prompt_with_context = """
Answer user question based on the provided context ONLY! If you don't know the answer, just say \"I don't know\".
### Context:
{context}

### Question:
{question}

### Answer:
"""

system_no_context = SystemMessagePromptTemplate.from_template(
    "You are a helpful AI assistant who answers user questions."
)
prompt_no_context = """
Answer the following question as best as you can. If you don't know the answer, just say \"I don't know\".
### Question:
{question}

### Answer:
"""

def get_chain(context):
    if context and context.strip():
        prompt = HumanMessagePromptTemplate.from_template(prompt_with_context)
        messages = [system_with_context, MessagesPlaceholder(variable_name="history"), prompt]
    else:
        prompt = HumanMessagePromptTemplate.from_template(prompt_no_context)
        messages = [system_no_context, MessagesPlaceholder(variable_name="history"), prompt]
    template = ChatPromptTemplate(messages)
    return template | llm | StrOutputParser()

def chat_with_llm(session_id, context, question):
    chain = get_chain(context)
    runnable = RunnableWithMessageHistory(
        chain, 
        get_session_history, 
        input_messages_key="question",
        history_messages_key="history"
    )
    inputs = {
        'context': context,
        'question': question
    }
    for output in runnable.stream(inputs, config={'configurable': {'session_id': session_id}}):
        yield output

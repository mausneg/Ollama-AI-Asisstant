import pymupdf
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from operator import itemgetter

class Assistant:
    def __init__(self, 
                 base_url="http://localhost:11434",
                 llm_model="llama3.2:3b",
                 embeddings_model="nomic-embed-text",
                 vector_db_path="vector_db",
                 chat_history_db="sqlite:///chat_history.db"):
        
        self.base_url = base_url
        self.llm_model = llm_model
        self.embeddings_model = embeddings_model
        self.vector_db_path = os.path.abspath(vector_db_path)
        self.chat_history_db = chat_history_db
        
        self.llm = ChatOllama(base_url=self.base_url, model=self.llm_model)
        self.embeddings = OllamaEmbeddings(model=self.embeddings_model, base_url=self.base_url)
        
        self.system_prompt_with_context = SystemMessagePromptTemplate.from_template(
            "You are a helpful AI assistant who answers user questions based on the provided context from documents."
        )
        
        self.prompt_template_with_context = """
        Answer the user's question based on the context below. If the context doesn't contain relevant information, say "I don't have enough information to answer that question."

        ### Context:
        {context}

        ### Question:
        {question}

        ### Answer:
        """
        
        self.system_prompt_no_context = SystemMessagePromptTemplate.from_template(
            "You are a helpful AI assistant."
        )
    
    def _format_docs(self, docs):
        return '\n\n'.join([doc.page_content for doc in docs])
    
    def _get_session_history(self, session_id):
        return SQLChatMessageHistory(session_id, self.chat_history_db)
    
    def convert_document(self, uploaded_file):
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in pdf:
                text += page.get_text()
            pdf.close()
            doc = Document(page_content=text, metadata={"source": uploaded_file.name})
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100
            )
            chunks = text_splitter.split_documents([doc])
            return chunks
        return None
    
    def vector_store_document(self, chunks):
        if chunks:
            if os.path.exists(self.vector_db_path):
                vector_store = FAISS.load_local(
                    self.vector_db_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                vector_store.add_documents(chunks)
            else:
                vector_store = FAISS.from_documents(chunks, self.embeddings)
            vector_store.save_local(self.vector_db_path)
            return True
        return False
    
    def vectorize_document(self, uploaded_file):
        chunks = self.convert_document(uploaded_file)
        return self.vector_store_document(chunks)
    
    def get_retriever(self):
        if os.path.exists(self.vector_db_path):
            vector_store = FAISS.load_local(
                self.vector_db_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            retriever = vector_store.as_retriever(
                search_type='similarity',
                search_kwargs={'k': 10, 'fetch_k': 30}
            )
            return retriever
        return None
    
    def chat(self, session_id, question):
        retriever = self.get_retriever()
        if retriever:
            prompt = HumanMessagePromptTemplate.from_template(self.prompt_template_with_context)
            messages = [self.system_prompt_with_context, MessagesPlaceholder(variable_name="history"), prompt]
            template = ChatPromptTemplate(messages=messages)
            
            chain = {
                "context": itemgetter("question") | retriever | self._format_docs, 
                "question": itemgetter("question"),
                "history": itemgetter("history")
            } | template | self.llm | StrOutputParser()
        else:
            simple_prompt = HumanMessagePromptTemplate.from_template("{question}")
            messages = [
                self.system_prompt_no_context,
                MessagesPlaceholder(variable_name="history"),
                simple_prompt
            ]
            template = ChatPromptTemplate(messages= messages)
            chain = template | self.llm | StrOutputParser()
        
        runnable = RunnableWithMessageHistory(
            chain, 
            self._get_session_history, 
            input_messages_key="question",
            history_messages_key="history"
        )

        inputs = {"question": question}
        for output in runnable.stream(inputs, config={'configurable': {'session_id': session_id}}):
            yield output

from collections import deque
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# CONFIGURATION
# ---------------------------------------------------------
VECTOR_STORE_PATH = "./chroma_db_bge"
EMBEDDING_MODEL_NAME = "bge-m3"
OLLAMA_MODEL = "mistral-nemo" 

chat_history = deque(maxlen=10)  # Store last 5 questions and answers

def format_chat_history(_):
    """
    Convert chat history deque to a single tagged string.
    """
    if not chat_history:
        return "No prior conversation."
    print(f'--- Debug: Formatting chat history with {len(chat_history)} entries ---')
    
    return "\n".join(chat_history)

class ChatManager:
    def __init__(self):
        # A. Load Embeddings
        print("--- [DEBUG] Loading Embeddings... ---")
        embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            base_url="http://127.0.0.1:11434"
        )

        # B. Load VectorDB
        print(f"--- [DEBUG] Loading VectorStore from {VECTOR_STORE_PATH}... ---")
        vectorstore = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=embeddings,
            collection_name="rag_corpus_bge"
        )

        # C. Create Retriever
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3}
        )

        # D. Setup LLM
        llm = ChatOllama(model=OLLAMA_MODEL, temperature=0, streaming=True, num_ctx=32_768)

        contextualize_template = """
            Based on the history and the new question, 
            write a single specific search query for a survival manual.
            History: {history}
            Question: {question}
            Search Query:
        """
        contextualize_prompt = ChatPromptTemplate.from_template(contextualize_template)
        contextualize_chain = (
            {"history": format_chat_history, "question": RunnablePassthrough()}
            | contextualize_prompt
            | llm
            | StrOutputParser()
        )

        # E. Create Prompt Template
        template = """
            You are a survival expert AI assistant. 
            Use the following pieces of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know.
            Do not make up answers.
            Context: {context}
            Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        # F. Build Chain
        def format_docs(docs):
            print(f'--- Debug: Retrieved {len(docs)} documents for the query ---')
            return "\n\n".join([d.page_content for d in docs])
        
        retrieval_chain = RunnableParallel(
            context=retriever | format_docs,
            docs=retriever,
            question=RunnablePassthrough(),
            printer=lambda x: print(f'--- Debug: Retrieval Chain Input Question: {x} ---')
        )

        self.rag_chain = (
            contextualize_chain
            | retrieval_chain
            | RunnableParallel(
                answer=prompt | llm | StrOutputParser(),
                docs=lambda x: x['docs']  # Pass through docs
            )
        )


if __name__ == "__main__":
    chat_manager = ChatManager()
    while True:
        query_text = input("Enter your query: ")

        full_answer = ''

        for chunk in chat_manager.rag_chain.stream(query_text):
            
            # Handle Answer Tokens
            if 'answer' in chunk:
                token = chunk['answer']
                full_answer += token
                print(token, end='', flush=True)
            
            # Handle Documents
            if 'docs' in chunk:
                docs = chunk['docs']
                print(f"\n\n[System] Found {len(docs)} sources:")
                for d in docs:
                    print(f" - {d.metadata.get('source', 'Unknown')}")
        print()  # For newline after streaming answer

        chat_history.append(f'[Human]: {query_text}')
        chat_history.append(f'[AI]: {full_answer}')
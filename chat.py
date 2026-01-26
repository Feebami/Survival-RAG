import os

from collections import deque
import chainlit as cl
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

# CONFIGURATION
# ---------------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH = os.path.join(base_dir, "data", "chroma_db_bge")
OLLAMA_MODEL = "llama3.1" 

chat_history = deque(maxlen=20)  # Store last 20 messages

def format_chat_history(_):
    """
    Convert chat history deque to a single tagged string.
    """
    if not chat_history:
        return "No prior conversation."
    
    return "\n".join(chat_history)

@cl.on_chat_start
async def on_chat_start():
    # A. Load Embeddings
    print("--- [DEBUG] Loading Embeddings... ---")
    embeddings = OllamaEmbeddings(
        model="bge-m3",
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
        search_kwargs={"k": 5}
    )
    cl.user_session.set("retriever", retriever)

    # D. Setup LLM
    llm = ChatOllama(model=OLLAMA_MODEL, temperature=0, streaming=True, num_ctx=16_384)

    contextualize_template = """
        Given a chat history and the latest user question, formulate a standalone question that can be understood without the chat history and includes all necessary context to effectively answer the question. 
        Do NOT answer the question, just reformulate it if needed.
        Based on the history and the new question, write a specific search query for a RAG corpus and LLM question answering.
        Chat History: {history}
        Question: {question}
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
        return "\n\n".join([d.page_content for d in docs])
    
    retrieval_chain = RunnableParallel(
        context=retriever | format_docs,
        docs=retriever,
        question=RunnablePassthrough(),
        printer=lambda x: print(f'--- Debug: Retrieval Chain Input Question: {x} ---')
    )

    rag_chain = (
        contextualize_chain
        | retrieval_chain
        | RunnableParallel(
            answer=prompt | llm | StrOutputParser(),
            docs=lambda x: x['docs']  # Pass through docs
        )
    )

    cl.user_session.set("rag_chain", rag_chain)
    await cl.Message(content="System ready! Ask me anything.").send()


@cl.on_message
async def on_message(message: cl.Message):
    rag_chain = cl.user_session.get("rag_chain")
    query_text = message.content 

    full_answer = ''

    msg = cl.Message(content="")

    
    async for chunk in rag_chain.astream(query_text):
        # Handle Answer Tokens
        if 'answer' in chunk:
            token = chunk['answer']
            full_answer += token
            await msg.stream_token(token)
        
        # Handle Documents
        if 'docs' in chunk:
            docs = chunk['docs']
            msg.elements = [cl.Text(
                name=f"Source_{i+1}({d.metadata.get('source', 'Unknown')})",
                content=d.page_content,
                display="side"
            ) for i, d in enumerate(docs)]
    msg.content += f'\n\n**Sources:** ' + ", ".join(
        [f"Source_{i+1}({d.metadata.get('source', 'Unknown')})" for i, d in enumerate(docs)]
    ) if docs else "\n\n(No sources found in database)"

    chat_history.append(f'[Human]: {query_text}')
    chat_history.append(f'[AI]: {full_answer}')

    await msg.update()

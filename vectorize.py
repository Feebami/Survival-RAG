import os
import glob
import shutil
import tqdm
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# CONFIGURATION
# ---------------------------------------------------------
CORPUS_PATH = 'data/cleaned_chunks'
TARGET_CHUNK_SIZE = 2000  # ~500 tokens
CHUNK_OVERLAP = 400       # 20% overlap to preserve context at edges
VECTOR_STORE_PATH = 'data/chroma_db_bge'

EMBEDDING_MODEL_NAME = 'bge-m3'

def split_text(folder_path):

    # 1. Define Hierarchy (The Logical Splitter)
    headers_to_split_on = [
        ("#", "H1"),
        ("##", "H2"),
        ("###", "H3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=TARGET_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        # Priority: Split by paragraph -> new line -> sentence -> word
        separators=["\n\n", "\n", ". ", " ", ""] 
    )

    final_docs = []
    original_chunks = 0
    print(f"Processing corpus from {folder_path}...")
    for filepath in glob.glob(os.path.join(folder_path, "*.md")):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # PASS 1: Split by Logic (Headers)
        # Result: [Document(page_content="...", metadata={'H1': 'Fire', 'H2': 'Starting Methods'})]
        header_splits = markdown_splitter.split_text(content)
        original_chunks += len(header_splits)

        # PASS 2: Split by Size (Recursive)
        # We iterate through the logical chunks. If they are small, we keep them.
        # If they are big, we split them further but COPY the metadata down.
        for split in header_splits:
            # Appends source filename to metadata for citation later
            split.metadata["source"] = os.path.basename(filepath)

            if len(split.page_content) > TARGET_CHUNK_SIZE:
                # This is a mega-chunk. Split it further.
                recursive_chunks = text_splitter.split_documents([split])
                final_docs.extend(recursive_chunks)
            else:
                # This chunk is already a good size. Keep it.
                final_docs.append(split)

    print("-" * 30)
    print(f"Original Chunks (Logical): {original_chunks}")
    print(f"Final Chunks (Physical):   {len(final_docs)}")
    print("-" * 30)

    return final_docs

def create_vector_store(docs):
    """
    Creates a local Chroma vector 
    """
    if not docs:
        print("No documents to process.")
        return None
    
    if os.path.exists(VECTOR_STORE_PATH):
        print(f'Removing existing vector store at {VECTOR_STORE_PATH}...')
        shutil.rmtree(VECTOR_STORE_PATH)

    print(f"Loading Ollama embedding model: {EMBEDDING_MODEL_NAME}...")
    
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        base_url="http://127.0.0.1:11434"
    )

    print('Initializing vector store...')

    vectorstore = Chroma(
        collection_name="rag_corpus_bge",
        embedding_function=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )

    BATCH_SIZE = 128
    print(f"Embedding {len(docs)} documents in batches of {BATCH_SIZE}...")

    for i in tqdm.tqdm(range(0, len(docs), BATCH_SIZE)):
        batch = docs[i:i + BATCH_SIZE]
        try:
            vectorstore.add_documents(batch)
        except Exception as e:
            print(f"Error adding document {i} from {batch[0].metadata.get('source', 'unknown source')}: {e}")
            print(batch[0].page_content[:1000])  # Print first 1000 chars for debugging
    
    print(f"Success! Vector store saved to: {VECTOR_STORE_PATH}")
    return vectorstore

if __name__ == '__main__':
    docs = split_text(CORPUS_PATH)
    if docs:
        create_vector_store(docs)
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

    # 1. Define Hierarchy
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
        separators=["\n\n", "\n", ". ", " ", ""] 
    )

    final_docs = []
    print(f"Processing corpus from {folder_path}...")
    
    for filepath in glob.glob(os.path.join(folder_path, "*.md")):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # PASS 1: Split by Logic (Headers)
        header_splits = markdown_splitter.split_text(content)

        # PASS 2: Split by Size (Recursive) & PREPEND CONTEXT
        for split in header_splits:
            # Add filename source
            split.metadata["source"] = os.path.basename(filepath)

            # Build a header string from metadata, e.g., "Manual > Safety > Fire"
            header_context = []
            for level in ["H1", "H2", "H3"]:
                if level in split.metadata:
                    header_context.append(split.metadata[level])
            
            # Create a context string to prepend
            if header_context:
                context_str = " > ".join(header_context) + "\n---\n"
            else:
                context_str = ""

            # Check if we need to split further
            if len(split.page_content) > TARGET_CHUNK_SIZE:
                recursive_chunks = text_splitter.split_documents([split])
                
                # Update EACH sub-chunk to include the header context
                for sub_chunk in recursive_chunks:
                    sub_chunk.page_content = context_str + sub_chunk.page_content
                    final_docs.append(sub_chunk)
            else:
                # Add context to the single chunk
                split.page_content = context_str + split.page_content
                final_docs.append(split)

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
    )

    print('Initializing vector store...')

    vectorstore = Chroma(
        collection_name="rag_corpus_bge",
        embedding_function=embeddings,
        persist_directory=VECTOR_STORE_PATH,
        collection_metadata={"hnsw:space": "cosine"}
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
import glob
import os
from langchain_text_splitters import MarkdownHeaderTextSplitter

# CONFIGURATION
# ---------------------------------------------------------
CORPUS_PATH = "md_corpus"
TARGET_CHUNK_SIZE = 1000  # ~250 tokens
CHUNK_OVERLAP = 200

# 1. Define Hierarchy
headers_to_split_on = [
    ("#", "H1"),
    ("##", "H2"),
    ("###", "H3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

# Helper function to reconstruct text with headers from metadata
def reconstruct_chunk(doc):
    text = doc.page_content
    # Prepend headers in reverse order (H3, then H2, then H1)
    if "H3" in doc.metadata:
        text = f"### {doc.metadata['H3']}\n{text}"
    if "H2" in doc.metadata:
        text = f"## {doc.metadata['H2']}\n{text}"
    if "H1" in doc.metadata:
        text = f"# {doc.metadata['H1']}\n{text}"
    return text

def process_splits(splits, file_name):
    # PASS 2: Merge Small Chunks
    # We work on a list of Documents directly so we can merge metadata if needed
    processed_splits = splits[:] 

    i = 0
    while i < len(processed_splits):
        current_doc = processed_splits[i]
        current_len = len(current_doc.page_content)
        
        # If chunk is too small, try to merge
        if current_len < TARGET_CHUNK_SIZE:
            
            # Define neighbors
            left_index = i - 1
            right_index = i + 1
            
            has_left = left_index >= 0
            has_right = right_index < len(processed_splits)
            
            merge_direction = None
            
            # DECISION LOGIC: Find smaller neighbor
            if has_left and has_right:
                len_left = len(processed_splits[left_index].page_content)
                len_right = len(processed_splits[right_index].page_content)
                
                if len_left < len_right:
                    merge_direction = 'left'
                else:
                    merge_direction = 'right'
            elif has_left:
                merge_direction = 'left'
            elif has_right:
                merge_direction = 'right'
            else:
                # Only one chunk exists, cannot merge
                break

            # EXECUTE MERGE
            if merge_direction == 'left':
                # Merge CURRENT into LEFT
                # We append current content to left neighbor's content
                # (Simple text merge; you might want to strip headers from the second part)
                processed_splits[left_index].page_content += "\n\n" + current_doc.page_content
                
                # Remove current node
                processed_splits.pop(i)
                # Adjust index: we removed 'i', so next iteration checks the new node at 'i' (originally i+1)
                # But since we merged backward, the 'left' node grew. We usually don't re-check the 'left' node immediately 
                # unless we want recursive merging. Let's decrement to re-check the 'left' node just in case it's still small.
                i -= 1 
                
            elif merge_direction == 'right':
                # Merge CURRENT into RIGHT
                # We prepend current content to right neighbor
                processed_splits[right_index].page_content = current_doc.page_content + "\n\n" + processed_splits[right_index].page_content
                
                # If you want to keep the headers of the "main" (larger) chunk, 
                # or the first chunk, you have to decide here. 
                # Usually keeping the first chunk's metadata is safer for flow.
                # We keep 'current' metadata if it's the start of the section.
                processed_splits[right_index].metadata.update(current_doc.metadata)

                # Remove current node
                processed_splits.pop(i)
                # Don't increment i; the node at 'i' is now the *new* merged node (previously right).
                # We want to check this new node in the next iteration.
                continue
                
        # Move to next chunk
        i += 1

    print(f"Number of chunks after merging: {len(processed_splits)}")

    # PASS 3: Formatting and Saving
    final_chunks = [reconstruct_chunk(doc) for doc in processed_splits]

    output_dir = "cleaned_chunks"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)

    # Open file ONCE outside the loop to write all chunks
    with open(output_path, 'w', encoding='utf-8') as f:
        for chunk in final_chunks:
            f.write(chunk + '\n\n')

    print(f"Saved merged chunks to {output_path}")


for filepath in glob.glob(os.path.join(CORPUS_PATH, "*.md")):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    splits = markdown_splitter.split_text(text.replace(' ', ' '))
    file_name = os.path.basename(filepath)
    print(f"Processing file: {file_name} with {len(splits)} initial chunks.")
    process_splits(splits, file_name)
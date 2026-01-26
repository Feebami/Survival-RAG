import os
import sys

def remove_string_from_md_files(folder_path, string_to_remove):
    """Remove all occurrences of a string from all .md files in a folder."""
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    
    if not md_files:
        print(f"No .md files found in '{folder_path}'.")
        return
    
    for filename in md_files:
        file_path = os.path.join(folder_path, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content.replace(string_to_remove, '')
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    
    folder_path = 'md_corpus'
    string_to_remove = '<!-- image -->'
    
    remove_string_from_md_files(folder_path, string_to_remove)
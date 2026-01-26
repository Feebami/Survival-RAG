import os
import sys

def remove_fluff_from_file(file_path):
    """Remove all lines with only capital letters"""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            # Check if the line is not empty and is not all uppercase (ignoring non-letter characters)
            if stripped_line and not all(char.isupper() or not char.isalpha() for char in stripped_line) or stripped_line.startswith('#'):
                new_lines.append(line)
        # Create new file to save new lines
        new_file_path = file_path.replace('.md', '_processed.md')
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        
        print(f"Processed: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error processing {os.path.basename(file_path)}: {e}")

if __name__ == "__main__":
    
    file_path = 'cleaned_chunks/THE BOOK OF CAMP LORE AND WOODCRAFT.md'
    
    remove_fluff_from_file(file_path)
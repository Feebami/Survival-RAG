import re
import sys

def convert_txt_to_md(input_file):
    output_file = input_file.replace('.txt', '.md')
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    result = []
    for i in range(len(lines)):
        line = lines[i]
        
        # Check if current line is all caps (excluding whitespace)
        stripped = line.strip()
        if stripped and stripped.isupper():
            # Check if sandwiched by blank lines
            prev_blank = (i == 0 or lines[i-1].strip() == '')
            next_blank = (i == len(lines)-1 or lines[i+1].strip() == '')
            
            if prev_blank and next_blank:
                result.append(f"# {line}")
            else:
                result.append(line)
        else:
            result.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(result)

if __name__ == '__main__':
    
    input_file = "corpus/THE WOODS AND THE TRICKS OF TRAPPING AND TRAP MAKING.txt"
    convert_txt_to_md(input_file)
    print(f"Converted {input_file} to markdown format.")
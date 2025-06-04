import re
import argparse
from pathlib import Path

def update_readme(table_path: Path, readme_path: Path):

    with open(table_path, "rb") as f:  
        new_table = f.read().strip()   
        

    with open(readme_path, "rb") as f:  
        readme_content = f.read()
    

    pattern = rb"<!-- CONSUMABLES_TABLE_START -->.*?<!-- CONSUMABLES_TABLE_END -->"  # Non-greedy match
    replacement = b"<!-- CONSUMABLES_TABLE_START -->\n" + new_table + b"\n<!-- CONSUMABLES_TABLE_END -->"
    
    # Replace content between markers
    updated_readme = re.sub(
        pattern, 
        replacement, 
        readme_content, 
        flags=re.DOTALL  # Makes '.' match newlines
    )
    
    with open(readme_path, "wb") as f:
        f.write(updated_readme)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("table_path", type=Path, help="Path to markdown table file")
    parser.add_argument("readme_path", type=Path, help="Path to README.md file")
    args = parser.parse_args()
    
    update_readme(args.table_path, args.readme_path)
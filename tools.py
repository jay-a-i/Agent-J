import os
from dotenv import load_dotenv
from pathlib import Path
from tavily import AsyncTavilyClient

load_dotenv()

tavily = AsyncTavilyClient(os.getenv("TAVILY_API_KEY"))

async def search_web(query: str):
    response = await tavily.search(
        query=query,
        max_results=3,
        search_depth='advanced')
    content_list = []
    for result in response['results']:
        content_list.append(f"Source: {result['url']}\nContent: {result['content']}")
    return "\n\n".join(content_list)

def read_file(file_path):
    try:
        output_lines = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                output_lines.append(f"{line_num:3} | {line}")      
        return "".join(output_lines)
    except FileNotFoundError:
        return "The file does not exist."

def list_directory(dir_path: str, indent_lvl=0, ignore_list=None, output=None):
    if output is None:
        output = []
    if ignore_list is None:
        ignore_list = {".git", ".gitignore", "__pycache__", ".vscode", ".DS_Store", "node_modules", ".venv", ".python-version"}
    try:
        path = Path(dir_path)
        spacer = "    " * indent_lvl
        if indent_lvl == 0:
            output.append(f"{path.name}/")
            indent_lvl += 1
            spacer = "    " * indent_lvl
        filtered_items = [x for x in path.iterdir() if x.name not in ignore_list]
        sorted_items = sorted(filtered_items, key=lambda x: (not x.is_dir(), x.name.lower()))
        for item in sorted_items:
            if item.is_dir():
                output.append(f"{spacer}{item.name}/")
                list_directory(str(item), indent_lvl + 1, ignore_list, output)
            else:
                output.append(f"{spacer}{item.name}")
    except (FileNotFoundError, PermissionError) as e:
        output.append(f"{spacer}[Error: {e.strerror}]")

    if indent_lvl <= 1:
        return "\n".join(output)
    
def write_file(file_path, content):
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            return f"Success: File successfully written at '{file_path}'"
    except Exception as e:
        return f"[Error Occured: {e}]"
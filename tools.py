
def read_file(file_path):
    try:
        output_lines = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                output_lines.append(f"{line_num:3} | {line}") 
        print(output_lines)       
        return "".join(output_lines)
    except FileNotFoundError:
        return "The file does not exist."
search_web_schema = {# "search_web" tool schema
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the internet for recent information, documentation, "
                "news, APIs, libraries, dates, and facts that are not available "
                "locally. Use this tool when up-to-date information is required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                    "type": "string",
                    "description": "Search query describing the information to find."
                    }
                },
                "required": ["query"]
            }
        }
    }

read_file_schema = {# Schema of tool 'read_file'
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a file and return its contents with line numbers. "
                "Use this before editing a file or when inspecting existing code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                    "type": "string",
                    "description": "Path to the file to read."
                    }
                },
                "required": ["file_path"]
            }
        }
    }

list_dirctory_schema = {# Schema of tool 'list_directory'
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": (
                "Recursively list files and folders inside a directory. "
                "Use this to explore the workspace structure before reading "
                "or creating files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Directory path to inspect. Use '.' for the current workspace."
                    }
                },
                "required": ["dir_path"]
            }
        }
    }

write_file_schema = {# Schema of tool 'write_file'
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create a new file or completely overwrite an existing file. "
                "Use this tool when creating files from scratch or replacing "
                "the entire contents of a file. "
                "Prefer edit_file for making partial modifications."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path of the file to create or overwrite."},
                    "content": {
                        "type": "string",
                        "description": "Complete contents to write into the file."
                    }
                },
                "required": [
                    "file_path",
                    "content"
                    ]
            }
        }
    }

edit_file_schema = {# Schema of tool 'edit_file'
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Modify part of an existing file by replacing one exact block "
                "of text with another. Prefer this tool instead of write_file "
                "when only a small section needs to change. "
                "old_content must exactly match text already present in the file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to modify."
                    },
                    "old_content": {
                        "type": "string",
                        "description": (
                            "Exact text currently present in the file that should "
                            "be replaced. Include indentation and line breaks exactly."
                        )
                    },
                    "new_content": {
                        "type": "string",
                        "description": "Replacement text."
                    }
                },
                "required": ["file_path", "old_content", "new_content"]
            }
        }
    }

grep_schema = {# Schema of tool 'grep'
        "type": "function",
        "function": {
             "name": "grep",
            "description": (
                "Search the workspace for text patterns, function names, "
                "class names, variables, imports, or error messages. "
                "Use this tool when you need to find where code is located "
                "before reading or editing files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Text pattern to search for."
                    },
                    "root_dir": {
                        "type": "string",
                        "description": "Directory to search recursively. Use '.' for the workspace."
                    },
                    "ext_filter": {
                        "type": "string",
                        "description": "Optional extension filter such as '.py' or '.js'."
                    }
                },
                "required": ["root_dir", "search_term"]
            }
        }
    }

import os
import json
import asyncio
from tools import search_web, read_file, list_directory, write_file, edit_file
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import TypedDict
load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
  )

tool_schema = [
    {# "search_web" tool schema
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
    },
    {# Schema of tool 'read_file'
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
    },
    {# Schema of tool 'list_directory'
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
    },
    {# Schema of tool 'write_tool'
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
    },
    {# Schema of tool 'edit_file'
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
                "required": [
                    "file_path",
                    "old_content",
                    "new_content"
                ]
            }
        }
    }
]

async def main(user_input):
  
  messages = [
    {"role": "user", "content": f"{user_input}"}
  ]

  stream = await client.chat.completions.create(
      model="nex-agi/nex-n2-pro:free",
      messages=messages,
      tools=tool_schema,
      tool_choice='auto',
      stream=True,
      extra_body={"reasoning": {"enabled": True}}
  )

  tool_call_detected = False
  tool_name = ""
  tool_arguments_stream = ""
  
  async for chunk in stream:
      if chunk.choices:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            
        tool_calls = chunk.choices[0].delta.tool_calls
        if tool_calls:
            tool_call_detected = True
            delta_tool = tool_calls[0]

            if delta_tool.function.name:
                tool_name += delta_tool.function.name
            if delta_tool.function.arguments:
                tool_arguments_stream += delta_tool.function.arguments
                print(".", end="", flush=True)

  if tool_call_detected:
    print(f"\n\n[Tool Triggered]: Model requested function '{tool_name}'")
    try:
        parsed_args = json.loads(tool_arguments_stream)

        if tool_name == "search_web":
            search_web_arg = parsed_args.get("query", "")
            print(f"[Tool Executing]: '{tool_name}' → \"{search_web_arg}\"")
        elif tool_name == "read_file":
            read_file_arg = parsed_args.get("file_path", "")
            print(f"[Tool Executing]: '{tool_name}' → \"{read_file_arg}\"")
        elif tool_name == "list_directory":
            list_directory_arg = parsed_args.get("dir_path", "")
            print(f"[Tool Executing]: '{tool_name}' → \"{list_directory_arg}\"")
        elif tool_name == "write_file":
            write_file_path = parsed_args.get("file_path", "")
            write_file_content = parsed_args.get("content", "")
            print(f"[Tool Executing]: '{tool_name}' → \"{write_file_path}\"")

        tools_result = []
        if tool_name == "search_web":
            search_web_result = await search_web(search_web_arg)
            tools_result.append({tool_name: search_web_result})
        elif tool_name == "read_file":
            read_file_result = read_file(read_file_arg)
            tools_result.append({tool_name: read_file_result})
        elif tool_name == "list_directory":
            list_directory_result = list_directory(list_directory_arg) 
            tools_result.append({tool_name: list_directory_result})
        elif tool_name == "write_file":
            write_file_result = write_file(write_file_path, write_file_content)
            tools_result.append({tool_name: write_file_result})

        call_id = "call_" + os.urandom(4).hex()

        messages.append({
              "role": "assistant", 
              "content": "", 
              "tool_calls": [{
                  "id": call_id, 
                  "type": "function",
                  "function": {"name": tool_name, "arguments": tool_arguments_stream}
              }]
          })
        messages.append({
              "role": "tool", 
              "tool_call_id": call_id, 
              "name": tool_name, 
              "content": json.dumps(tools_result[0])
              })

        messages.append({
                "role": "system",
                "content": "Answer the user's question directly using the context data given above."
            })

        print("[System]: Sending context back to model for final answer...\n")
        final_stream = await client.chat.completions.create(
            model="openai/gpt-oss-120b:free",
            messages=messages,
            stream=True,
            extra_body={"reasoning": {"enabled": True}})
          
        async for chunk in final_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                 
    except json.JSONDecodeError:
        print("\n[Error]: Failed to parse tool argument strings from model.")
          
  print()

class AgentState(TypedDict):
    messages: list
    retry_count: int
    current_step: str
    workspace: str

if __name__ == "__main__":
    user_input = input("Enter a prompt:  ")
    asyncio.run(main(user_input=user_input))
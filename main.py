import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import TypedDict
from sys_prompts import system_prompt
from tools import (search_web, read_file,
                   list_directory, write_file,
                   edit_file, grep)
from tool_schemas import (search_web_schema, read_file_schema,
                          list_dirctory_schema, write_file_schema,
                          edit_file_schema, grep_schema)

load_dotenv()

fol = [] # 'fol' stands for FinalOutputlog, making this now for future ReACT usecases.

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
  )

tool_schema = [search_web_schema, read_file_schema,
               list_dirctory_schema, write_file_schema,
               edit_file_schema, grep_schema
               ]

async def main(user_input):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_input
        }
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
        elif tool_name == 'edit_file':
            edit_file_path = parsed_args.get("file_path", "")
            edit_file_old_content = parsed_args.get("old_content", "")
            edit_file_new_content = parsed_args.get("new_content", "")
            print(f"[Tool Executing]: '{tool_name}' → File Path: \"{edit_file_path}\"")
        elif tool_name == 'grep':
            grep_root_dir = parsed_args.get("root_dir", "")
            grep_search_term = parsed_args.get("search_term", "")
            print(f"[Tool Executing]: '{tool_name}' → Root Directory:\"{grep_root_dir}\"\nSearch Term: \"{grep_search_term}\"")
            

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
        elif tool_name == "edit_file":
            edit_file_result = edit_file(edit_file_path, edit_file_old_content, edit_file_new_content)
            tools_result.append({tool_name: edit_file_result})
        elif tool_name == "grep":
            grep_result = grep(grep_root_dir, grep_search_term)
            tools_result.append({tool_name: grep_result})

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

#This is for future usecases.
class AgentState(TypedDict):
    messages: list
    retry_count: int
    current_step: str
    workspace: str

if __name__ == "__main__":
    user_input = input("Enter a prompt:  ")
    asyncio.run(main(user_input=user_input))
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, InMemorySessionStore, query
import asyncio
from helper import parse_message, MODEL_NAME
from pathlib import Path
import os
from claude_agent_sdk.types import (
    PermissionResultAllow, 
    PermissionResultDeny, 
    ToolPermissionContext
)

PROJECT_DIR = Path(__file__).resolve().parent
FILE_PATH = PROJECT_DIR / "requiredsoftware.csv"

# 1. Define the callback function
async def custom_tool_checker(
    tool_name: str, 
    input_data: dict, 
    context: ToolPermissionContext
) -> PermissionResultAllow | PermissionResultDeny:
    
    print(f"\nTool Requested: {tool_name}")
    print(f"Inputs: {input_data}")
    
    # Simple console approval check
    user_response = input("Allow Claude to run this tool? (y/n): ")
    
    if user_response.lower() == 'y':
        return PermissionResultAllow(behavior='allow')
    else:
        return PermissionResultDeny(behavior='deny', reason="User rejected the tool execution.")

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is missing from .env")

    if not workspace_id:
        raise ValueError("ANTHROPIC_WORKSPACE_ID is missing from .env")
        
    options = ClaudeAgentOptions(
        system_prompt="You are an helpful assistant",
        setting_sources=[],
        model=MODEL_NAME,
        max_turns=30,
        tools=["Read", "Glob", "Edit", "Write"],
        permission_mode="default",
        cwd=str(PROJECT_DIR),
        can_use_tool=custom_tool_checker,
        env={
            "ANTHROPIC_API_KEY": api_key,
            "ANTHROPIC_WORKSPACE_ID": workspace_id,
            "ANTHROPIC_CUSTOM_HEADERS":
                f"anthropic-workspace-id: {workspace_id}",
        }
        
    )
    async with ClaudeSDKClient(options=options) as client:
        question = input("Give any instruction:\n")
        #question = "Delete all the files from the directory"
        await client.query(question)
        async for messages in client.receive_messages():
            parse_message(messages)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())

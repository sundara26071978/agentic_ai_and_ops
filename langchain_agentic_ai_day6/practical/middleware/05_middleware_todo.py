import os
import subprocess
import tempfile

from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.tools import tool

from rich import print as rprint
from langchain.chat_models import init_chat_model


from dotenv import load_dotenv

load_dotenv()


model_basic = init_chat_model("nvidia/nemotron-3-ultra-550b-a55b:free",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=1000, temperature=0.0)

model_medium = init_chat_model("openai/gpt-5.6-luna",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)

model_advanced = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)



@tool(parse_docstring=True)
def create_file(filename: str, content: str) -> str:
    """Create a new file with the given content.

    Args:
        filename: Name of the file to create.
        content: Content to write to the file.

    Returns:
        Confirmation message.
    """
    # Create in a temp directory for demo purposes
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, "w") as f:
        f.write(content)
    return f"Created {file_path} successfully"


@tool(parse_docstring=True)
def run_command(command: str) -> str:
    """Run a shell command and return the output.

    Args:
        command: Shell command to execute.

    Returns:
        Command output.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,  # noqa: S602
            capture_output=True,
            text=True,
            timeout=10,
            cwd=tempfile.gettempdir(),
        )
        if result.returncode == 0:
            return f"Command succeeded:\n{result.stdout}"
        return f"Command failed (exit code {result.returncode}):\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds"
    except Exception as e:
        return f"Error running command: {e}"


agent = create_agent(
    model=model_advanced,
    tools=[create_file, run_command],
    system_prompt="You are a software development assistant.",
    middleware=[TodoListMiddleware()],
)
print("-"*50)
print("Todo list middleware")
print("-"*50)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": """
            create hello.sh and goodbye.sh scripts make them both executable and ensure they exists
            """
        }
    ]
},  
config={
        "run_name": "todo list middleware",      # Custom name for this run
        "tags": ["todo", "agentplanning","agenttracking"],          # Tags for categorization
        "metadata": {"user_id": "sunjtodo"},     # Custom metadata
      
    })

print("-"*50)
rprint(result)
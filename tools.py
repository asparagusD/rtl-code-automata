import os
import subprocess
import platform

def run_iverilog(file_path: str) -> str:
    """
    Runs iverilog on the given Verilog file and returns the output (errors/warnings).
    """
    executable = "iverilog.exe" if platform.system() == "Windows" else "iverilog"
    try:
        # iverilog -t null file_path
        # -o os.devnull parses and checks the file without writing an executable
        result = subprocess.run(
            [executable, "-o", os.devnull, file_path],
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout + result.stderr
        if not output.strip():
            return "Success: No errors or warnings."
        return output
    except FileNotFoundError:
        return f"Error: '{executable}' not found. Please ensure it is installed and in your PATH."
    except Exception as e:
        return f"Error running iverilog: {str(e)}"

def read_file(file_path: str) -> str:
    """
    Reads and returns the contents of a file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def write_file(file_path: str, new_content: str) -> str:
    """
    Writes new content to a file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"Successfully updated {file_path}."
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"

# OpenAI Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_iverilog",
            "description": "Run iverilog to perform syntax and compilation checks on a Verilog file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the Verilog file to check."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the current contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to read."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write completely new content to a file, replacing its current contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to modify."
                    },
                    "new_content": {
                        "type": "string",
                        "description": "The new content to write into the file."
                    }
                },
                "required": ["file_path", "new_content"]
            }
        }
    }
]

# Map names to functions for easy dispatch
TOOL_MAP = {
    "run_iverilog": run_iverilog,
    "read_file": read_file,
    "write_file": write_file,
}

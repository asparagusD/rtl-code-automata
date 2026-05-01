import json
from rich.console import Console
from rich.panel import Panel

from llm import chat_completion
from tools import TOOLS, TOOL_MAP
from prompts import REVIEW_SYSTEM_PROMPT, REVIEW_USER_PROMPT

console = Console()

def run_review_agent(file_path: str, max_iter: int = 5):
    """
    Runs the LLM-driven review agent loop for the given file.
    """
    console.print(f"[bold blue]Starting RTL Code Review Agent for '{file_path}' (Max iterations: {max_iter})[/bold blue]")
    
    messages = [
        {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
        {"role": "user", "content": REVIEW_USER_PROMPT.format(file_path=file_path)}
    ]
    
    iteration = 1
    
    while iteration <= max_iter:
        console.print(f"\n[bold yellow]--- Iteration {iteration} / {max_iter} ---[/bold yellow]")
        
        console.print("[dim]Waiting for LLM response...[/dim]")
        
        # Call the LLM
        response_msg = chat_completion(messages, tools=TOOLS)
        messages.append(response_msg)
        
        if response_msg.content:
            console.print(Panel(response_msg.content, title="[green]Gemini[/green]", border_style="green"))
            
        # Check if the LLM made any tool calls
        if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Format arguments nicely for display
                args_display = {k: v if len(str(v)) < 100 else f"{str(v)[:100]}..." for k, v in args.items()}
                console.print(f"[bold cyan]Tool Call:[/bold cyan] {fn_name}({args_display})")
                
                # Execute the tool
                if fn_name in TOOL_MAP:
                    try:
                        result = TOOL_MAP[fn_name](**args)
                    except Exception as e:
                        result = f"Error executing {fn_name}: {str(e)}"
                else:
                    result = f"Error: Tool '{fn_name}' not found."
                
                # Show result (truncated if too long)
                result_display = str(result)
                if len(result_display) > 500:
                    result_display = result_display[:500] + "\n...[truncated]"
                console.print(f"[bold magenta]Tool Result:[/bold magenta]\n{result_display}")
                
                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(result)
                })
        else:
            # If no tool calls and no more work needed, break
            console.print("[bold green]Agent has finished reviewing the file.[/bold green]")
            break
            
        iteration += 1

    if iteration > max_iter:
        console.print("[bold red]Reached maximum iterations without completion.[/bold red]")


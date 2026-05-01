import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm import chat_completion
from tools import TOOLS, TOOL_MAP
from prompts import REVIEW_SYSTEM_PROMPT, REVIEW_USER_PROMPT

console = Console()

def run_review_agent(file_path: str, max_iter: int = 12):
    """
    Runs the LLM-driven review agent loop for the given file.
    """
    console.print(f"[bold blue]Starting RTL Code Review Agent for '{file_path}' (Max iterations: {max_iter})[/bold blue]")
    
    messages = [
        {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
        {"role": "user", "content": REVIEW_USER_PROMPT.format(file_path=file_path)}
    ]
    
    iteration = 1
    tool_calls_count = 0
    final_status = "Pending"
    
    while iteration <= max_iter:
        console.print(f"\n[bold yellow]--- Iteration {iteration} / {max_iter} ---[/bold yellow]")
        
        console.print("[dim]Waiting for LLM response...[/dim]")
        
        # Call the LLM
        response_msg = chat_completion(messages, tools=TOOLS)
        messages.append(response_msg)
        
        if response_msg.content:
            console.print(Panel(response_msg.content, title="[green]Agent[/green]", border_style="green"))
            
        # Check if the LLM made any tool calls
        if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                tool_calls_count += 1
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
                
                if "Success: No errors or warnings" in result_display:
                    console.print(f"[bold green]Tool Result:[/bold green]\n[green]{result_display}[/green]")
                elif "Error" in result_display or "syntax error" in result_display:
                    console.print(f"[bold red]Tool Result:[/bold red]\n[red]{result_display}[/red]")
                else:
                    console.print(f"[bold magenta]Tool Result:[/bold magenta]\n{result_display}")
                
                # Append tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(result)
                })
        else:
            # If no tool calls made at all, force a review
            if tool_calls_count == 0:
                console.print("[yellow]⚠ Agent made no tool calls — forcing review[/yellow]")
                messages.append({
                    "role": "user",
                    "content": "You must call read_file and run_iverilog before finishing. Please review the file now."
                })
                iteration += 1
                continue
            # If tool calls were made previously and no more needed, break
            console.print("[bold green]Agent has finished reviewing the file.[/bold green]")
            final_status = "Success (Clean)"
            break
            
        iteration += 1

    if iteration > max_iter:
        console.print("[bold red]Reached maximum iterations without completion.[/bold red]")
        final_status = "Failed (Max Iterations)"

    # Print summary table
    table = Table(title="RTL Code Review Summary", border_style="blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    table.add_row("File Reviewed", file_path)
    table.add_row("Total Iterations", str(min(iteration, max_iter)))
    table.add_row("Tool Calls Made", str(tool_calls_count))
    status_color = "green" if "Success" in final_status else "red"
    table.add_row("Final Status", f"[{status_color}]{final_status}[/{status_color}]")
    
    console.print("\n")
    console.print(table)


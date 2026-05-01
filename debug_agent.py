import os
import json
import datetime
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm import chat_completion
from tools import read_file
from waveform_parser import get_waveform_summary, get_signal_transitions
from prompts import DEBUG_SYSTEM_PROMPT, DEBUG_USER_PROMPT

console = Console()

def write_report(content: str, out_dir: str = None) -> str:
    """
    Saves the report to the outputs directory.
    """
    if not out_dir:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join("outputs", timestamp)
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "debug_report.md")
    
    # Inject real dynamic timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = re.sub(r"## Timestamp:.*", f"## Timestamp: {current_time}", content)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Report successfully saved to {report_path}"

def run_debug_agent(vcd_path: str, rtl_path: str, out_dir: str, max_iter: int = 12):
    """
    Runs the LLM-driven debug agent loop.
    """
    console.print(f"[bold blue]Starting Waveform Debugger Agent[/bold blue]")
    console.print(f"  [cyan]RTL:[/cyan] {rtl_path}")
    console.print(f"  [cyan]VCD:[/cyan] {vcd_path}")
    
    def _write_report(report_content: str) -> str:
        return write_report(report_content, out_dir=out_dir)
        
    DEBUG_TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file to read."}
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_waveform_summary",
                "description": "Returns a structured summary of the VCD file including identified anomalies like X/Z states or stuck signals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vcd_path": {"type": "string", "description": "Path to the VCD file."}
                    },
                    "required": ["vcd_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_signal_transitions",
                "description": "Returns the detailed transition history for a specific signal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vcd_path": {"type": "string", "description": "Path to the VCD file."},
                        "signal_name": {"type": "string", "description": "Name of the signal to inspect."}
                    },
                    "required": ["vcd_path", "signal_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_report",
                "description": "Saves the generated markdown debug report to the outputs directory. Ends the debug session.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_content": {"type": "string", "description": "The markdown content of the bug report."}
                    },
                    "required": ["report_content"]
                }
            }
        }
    ]
    
    DEBUG_TOOL_MAP = {
        "read_file": read_file,
        "get_waveform_summary": get_waveform_summary,
        "get_signal_transitions": get_signal_transitions,
        "write_report": _write_report
    }

    messages = [
        {"role": "system", "content": DEBUG_SYSTEM_PROMPT},
        {"role": "user", "content": DEBUG_USER_PROMPT.format(vcd_path=vcd_path, rtl_path=rtl_path)}
    ]
    
    iteration = 1
    tool_calls_count = 0
    final_status = "Pending"
    report_written = False
    
    while iteration <= max_iter:
        console.print(f"\n[bold yellow]--- Iteration {iteration} / {max_iter} ---[/bold yellow]")
        
        if iteration == max_iter:
            console.print("[bold red]Injecting FINAL ITERATION warning to LLM...[/bold red]")
            messages.append({"role": "system", "content": "FINAL ITERATION: You MUST call write_report now with all findings. Do not call any other tools."})
            
        console.print("[dim]Waiting for LLM response...[/dim]")
        
        response_msg = chat_completion(messages, tools=DEBUG_TOOLS)
        messages.append(response_msg)
        
        if response_msg.content:
            console.print(Panel(response_msg.content, title="[green]Agent[/green]", border_style="green"))
            
        if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                tool_calls_count += 1
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                args_display = {k: v if len(str(v)) < 100 else f"{str(v)[:100]}..." for k, v in args.items()}
                console.print(f"[bold cyan]Tool Call:[/bold cyan] {fn_name}({args_display})")
                
                if fn_name in DEBUG_TOOL_MAP:
                    try:
                        result = DEBUG_TOOL_MAP[fn_name](**args)
                    except Exception as e:
                        result = f"Error executing {fn_name}: {str(e)}"
                else:
                    result = f"Error: Tool '{fn_name}' not found."
                
                result_display = str(result)
                if len(result_display) > 500:
                    result_display = result_display[:500] + "\n...[truncated]"
                
                if fn_name == "write_report":
                    console.print(f"[bold green]Tool Result:[/bold green]\n[green]{result_display}[/green]")
                    report_written = True
                elif "Error" in result_display:
                    console.print(f"[bold red]Tool Result:[/bold red]\n[red]{result_display}[/red]")
                else:
                    console.print(f"[bold magenta]Tool Result:[/bold magenta]\n{result_display}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(result)
                })
                
                if report_written:
                    break
        else:
            if not report_written:
                console.print("[bold red]Agent stopped without writing a report.[/bold red]")
                final_status = "Failed (No Report)"
            break
            
        if report_written:
            console.print("[bold green]Agent successfully wrote the debug report and finished.[/bold green]")
            final_status = "Success (Report Written)"
            break
            
        iteration += 1

    if iteration > max_iter and not report_written:
        console.print("[bold red]Reached maximum iterations without completion.[/bold red]")
        final_status = "Failed (Max Iterations)"

    table = Table(title="Waveform Debug Summary", border_style="blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    table.add_row("RTL File", rtl_path)
    table.add_row("VCD File", vcd_path)
    table.add_row("Total Iterations", str(min(iteration, max_iter)))
    table.add_row("Tool Calls Made", str(tool_calls_count))
    status_color = "green" if "Success" in final_status else "red"
    table.add_row("Final Status", f"[{status_color}]{final_status}[/{status_color}]")
    
    console.print("\n")
    console.print(table)

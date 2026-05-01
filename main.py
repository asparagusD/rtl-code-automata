import os
import sys
import argparse
import datetime
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

from agent import run_review_agent
from llm import chat_completion
from prompts import (
    GENERATE_RTL_SYSTEM_PROMPT,
    GENERATE_RTL_USER_PROMPT,
    GENERATE_TB_SYSTEM_PROMPT,
    GENERATE_TB_USER_PROMPT,
)

console = Console()

def validate_verilog_output(content: str, spec: str) -> bool:
    """Check if generated content is valid non-empty Verilog."""
    if not content or len(content.strip()) < 50:
        return False
    if "module" not in content:
        return False
    return True

def preflight_check(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding="utf-8") as f:
            content = f.read()
        if len(content.strip()) < 50:
            console.print(f"[red]✗ Pre-flight failed: {filepath} is empty or too short.[/red]")
            return False
        if "module" not in content:
            console.print(f"[red]✗ Pre-flight failed: {filepath} contains no Verilog module.[/red]")
            return False
        console.print(f"[green]✓ Pre-flight passed: {filepath} looks valid.[/green]")
        return True
    except FileNotFoundError:
        console.print(f"[red]✗ Pre-flight failed: {filepath} not found.[/red]")
        return False

def main():
    parser = argparse.ArgumentParser(description="Agentic RTL Design Automation Pipeline")
    parser.add_argument("--review", type=str, help="Path to the Verilog file to review and fix (Part 1)")
    parser.add_argument("--generate", action="store_true", help="Generate RTL from spec (Part 2)")
    parser.add_argument("--spec", type=str, help="Plain English block description for generation (Part 2)")
    parser.add_argument("--debug", action="store_true", help="Debug waveform anomalies (Waveform Debugger Agent)")
    parser.add_argument("--vcd", type=str, help="Path to the VCD waveform file for --debug")
    parser.add_argument("--rtl", type=str, help="Path to the RTL source file for --debug")
    parser.add_argument("--max-iter", type=int, default=8, help="Maximum iterations for the agent loop")
    parser.add_argument("--output", type=str, default="outputs", help="Base directory for generated outputs (default: outputs/)")
    parser.add_argument("--simulate", action="store_true", help="Automatically compile and simulate generated RTL via WSL2")
    parser.add_argument("--dir", type=str, help="Output directory to simulate (when using standalone --simulate)")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENROUTER_API_KEY"):
        console.print("[bold red]Error: OPENROUTER_API_KEY environment variable not set.[/bold red]")
        console.print("Please set it in your .env file or environment.")
        return

    if args.review:
        if not os.path.exists(args.review):
            console.print(f"[bold red]Error: File '{args.review}' not found.[/bold red]")
            return
        run_review_agent(args.review, args.max_iter)
    elif args.generate:
        if not args.spec:
            console.print("[bold red]Error: --spec is required when using --generate.[/bold red]")
            return
        console.print(f"[bold blue]Generating RTL from spec: '{args.spec}'[/bold blue]")
        
        # 1. Generate timestamped directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(args.output, timestamp)
        os.makedirs(out_dir, exist_ok=True)
        
        # 2. Call LLM for RTL
        console.print("[dim]Generating Verilog code...[/dim]")
        rtl_messages = [
            {"role": "system", "content": GENERATE_RTL_SYSTEM_PROMPT},
            {"role": "user", "content": GENERATE_RTL_USER_PROMPT.format(spec=args.spec)}
        ]
        for attempt in range(3):
            rtl_response = chat_completion(rtl_messages, max_tokens=8192)
            rtl_code = (rtl_response.content or "").strip()
            if validate_verilog_output(rtl_code, args.spec):
                break
            console.print(f"[yellow]⚠ Empty or invalid RTL generated (attempt {attempt+1}/3) — retrying...[/yellow]")
        else:
            console.print("[red]✗ Failed to generate valid RTL after 3 attempts. Aborting.[/red]")
            sys.exit(1)
        
        rtl_file = os.path.join(out_dir, "design.v")
        with open(rtl_file, "w", encoding="utf-8") as f:
            f.write(rtl_code)
        console.print(f"[bold green]Saved generated RTL to {rtl_file}[/bold green]")
        
        # 3. Call LLM for Testbench
        console.print("[dim]Generating Verilog testbench...[/dim]")
        tb_messages = [
            {"role": "system", "content": GENERATE_TB_SYSTEM_PROMPT},
            {"role": "user", "content": GENERATE_TB_USER_PROMPT.format(rtl_code=rtl_code)}
        ]
        for attempt in range(3):
            tb_response = chat_completion(tb_messages, max_tokens=8192)
            tb_code = (tb_response.content or "").strip()
            if validate_verilog_output(tb_code, rtl_code):
                break
            console.print(f"[yellow]⚠ Empty or invalid RTL generated (attempt {attempt+1}/3) — retrying...[/yellow]")
        else:
            console.print("[red]✗ Failed to generate valid RTL after 3 attempts. Aborting.[/red]")
            sys.exit(1)
        
        tb_file = os.path.join(out_dir, "tb_design.v")
        with open(tb_file, "w", encoding="utf-8") as f:
            f.write(tb_code)
        console.print(f"[bold green]Saved generated testbench to {tb_file}[/bold green]")
        
        # 4. Pipe RTL into Part 1 review loop
        console.print("\n[bold magenta]Piping generated RTL into Code Review Agent...[/bold magenta]")
        if not preflight_check(rtl_file):
            sys.exit(1)
        run_review_agent(rtl_file, args.max_iter)
        
        # 5. Simulate if requested
        if args.simulate:
            console.print("\n[bold magenta]Starting automated simulation pipeline...[/bold magenta]")
            from simulator import compile_and_simulate
            vcd_path = compile_and_simulate(out_dir)
            if vcd_path:
                console.print("\n[bold magenta]Piping VCD into Debug Agent...[/bold magenta]")
                from debug_agent import run_debug_agent
                run_debug_agent(vcd_path, rtl_file, out_dir, args.max_iter)
    elif args.simulate and not args.generate:
        if not args.dir:
            console.print("[bold red]Error: --dir is required for standalone --simulate.[/bold red]")
            return
        if not os.path.exists(args.dir):
            console.print(f"[bold red]Error: Directory '{args.dir}' not found.[/bold red]")
            return
            
        from simulator import compile_and_simulate
        vcd_path = compile_and_simulate(args.dir)
        if vcd_path:
            console.print("\n[bold magenta]Piping VCD into Debug Agent...[/bold magenta]")
            rtl_file = os.path.join(args.dir, "design.v")
            from debug_agent import run_debug_agent
            run_debug_agent(vcd_path, rtl_file, args.dir, args.max_iter)
    elif args.debug:
        if not args.vcd or not args.rtl:
            console.print("[bold red]Error: --vcd and --rtl are required when using --debug.[/bold red]")
            return
        if not os.path.exists(args.vcd):
            console.print(f"[bold red]Error: VCD file '{args.vcd}' not found.[/bold red]")
            return
        if not os.path.exists(args.rtl):
            console.print(f"[bold red]Error: RTL file '{args.rtl}' not found.[/bold red]")
            return
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(args.output, timestamp)
        os.makedirs(out_dir, exist_ok=True)
        
        from debug_agent import run_debug_agent
        run_debug_agent(args.vcd, args.rtl, out_dir, args.max_iter)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

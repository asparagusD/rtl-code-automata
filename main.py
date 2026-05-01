import os
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

def main():
    parser = argparse.ArgumentParser(description="Agentic RTL Design Automation Pipeline")
    parser.add_argument("--review", type=str, help="Path to the Verilog file to review and fix (Part 1)")
    parser.add_argument("--generate", action="store_true", help="Generate RTL from spec (Part 2)")
    parser.add_argument("--spec", type=str, help="Plain English block description for generation (Part 2)")
    parser.add_argument("--max-iter", type=int, default=5, help="Maximum iterations for the agent loop")
    parser.add_argument("--output", type=str, default="outputs", help="Base directory for generated outputs (default: outputs/)")
    
    args = parser.parse_args()
    
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Error: GOOGLE_API_KEY environment variable not set.[/bold red]")
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
        
        # 2. Call Gemini for RTL
        console.print("[dim]Generating Verilog code...[/dim]")
        rtl_messages = [
            {"role": "system", "content": GENERATE_RTL_SYSTEM_PROMPT},
            {"role": "user", "content": GENERATE_RTL_USER_PROMPT.format(spec=args.spec)}
        ]
        rtl_response = chat_completion(rtl_messages, max_tokens=8192)
        rtl_code = rtl_response.content.strip()
        
        rtl_file = os.path.join(out_dir, "design.v")
        with open(rtl_file, "w", encoding="utf-8") as f:
            f.write(rtl_code)
        console.print(f"[bold green]Saved generated RTL to {rtl_file}[/bold green]")
        
        # 3. Call Gemini for Testbench
        console.print("[dim]Generating cocotb testbench...[/dim]")
        tb_messages = [
            {"role": "system", "content": GENERATE_TB_SYSTEM_PROMPT},
            {"role": "user", "content": GENERATE_TB_USER_PROMPT.format(rtl_code=rtl_code)}
        ]
        tb_response = chat_completion(tb_messages, max_tokens=8192)
        tb_code = tb_response.content.strip()
        
        tb_file = os.path.join(out_dir, "test_design.py")
        with open(tb_file, "w", encoding="utf-8") as f:
            f.write(tb_code)
        console.print(f"[bold green]Saved generated testbench to {tb_file}[/bold green]")
        
        # 4. Pipe RTL into Part 1 review loop
        console.print("\n[bold magenta]Piping generated RTL into Code Review Agent...[/bold magenta]")
        run_review_agent(rtl_file, args.max_iter)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

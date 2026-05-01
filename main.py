import os
import argparse
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

from agent import run_review_agent

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Agentic RTL Design Automation Pipeline")
    parser.add_argument("--review", type=str, help="Path to the Verilog file to review and fix (Part 1)")
    parser.add_argument("--generate", action="store_true", help="Generate RTL from spec (Part 2)")
    parser.add_argument("--spec", type=str, help="Plain English block description for generation (Part 2)")
    parser.add_argument("--max-iter", type=int, default=5, help="Maximum iterations for the agent loop")
    
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
        console.print("[bold yellow]Generation (Part 2) is not fully implemented yet.[/bold yellow]")
        # Part 2 will be here later
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

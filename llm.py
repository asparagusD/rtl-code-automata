import os
import time
import openai
from openai import OpenAI
from rich.console import Console

console = Console()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

PRIMARY_MODEL = "tencent/hy3-preview:free"
FALLBACK_MODEL = "inclusionai/ling-2.6-1t:free"

def chat_completion(messages, tools=None, max_tokens=None):
    kwargs = {"messages": messages}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    else:
        kwargs["max_tokens"] = 8192

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"


    fallback = False
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=PRIMARY_MODEL, **kwargs
            )
            return response.choices[0].message
        except Exception as e:
            error_str = str(e).lower()
            if isinstance(e, openai.RateLimitError) or "quota" in error_str or "rate limit" in error_str:
                fallback = True
                break
            if attempt == 2:
                fallback = True
                break
            time.sleep(1)

    if fallback:
        console.print("[yellow]⚠ Hy3 rate limit — switching to Ling-2.6-1T fallback[/yellow]")
        # Fallback: Ling-2.6-1T
        try:
            response = client.chat.completions.create(
                model=FALLBACK_MODEL, **kwargs
            )
            return response.choices[0].message
        except Exception as e:
            console.print("[red]✗ Both providers failed.[/red]")
            raise

# Startup message
console.print("[green]✓ LLM ready: Hy3 (primary) + Ling-2.6-1T (fallback)[/green]")

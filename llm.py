import os
import time
import openai
from openai import OpenAI
from rich.console import Console

console = Console()

console.print("[green][OK] LLM ready: Gemini 2.5 Flash-Lite (primary) + Hy3 OpenRouter (fallback)[/green]")

gemini_client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

hy3_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

GEMINI_MODEL = "gemini-2.5-flash-lite"
HY3_MODEL = "tencent/hy3-preview:free"

def chat_completion(messages, tools=None, max_tokens=None):
    kwargs = {"messages": messages}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    # Try primary: Gemini 2.5 Flash-Lite
    fallback = False
    for attempt in range(3):
        try:
            response = gemini_client.chat.completions.create(
                model=GEMINI_MODEL, **kwargs
            )
            return response.choices[0].message
        except Exception as e:
            error_str = str(e).lower()
            if isinstance(e, openai.RateLimitError) or "quota" in error_str or "resource_exhausted" in error_str:
                fallback = True
                break
            if attempt == 2:
                fallback = True
                break
            time.sleep(1)
            
    if fallback:
        console.print("[yellow]⚠ Gemini quota hit — switching to Hy3 fallback (OpenRouter)[/yellow]")
        # Fallback: Hy3 on OpenRouter
        try:
            response = hy3_client.chat.completions.create(
                model=HY3_MODEL, **kwargs
            )
            return response.choices[0].message
        except Exception as e:
            console.print("[red]✗ Both providers failed.[/red]")
            raise

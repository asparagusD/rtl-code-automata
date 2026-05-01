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

def chat_completion_generate(messages):
    """Pure generation call — no tools.
    Forces the model to output text only."""

    def _extract_content(response):
        """Try all possible content locations in the response."""
        choice = response.choices[0]

        # Log everything for debugging
        console.print(f"[dim]finish_reason: {choice.finish_reason}[/dim]")
        console.print(f"[dim]message.content type: {type(choice.message.content)}[/dim]")
        console.print(f"[dim]message.content repr: {repr(choice.message.content)[:100]}[/dim]")
        console.print(f"[dim]usage: {response.usage}[/dim]")

        # Try all possible content locations
        content = (
            choice.message.content                      # standard location
            or getattr(choice.message, 'text', None)    # some providers
            or getattr(choice, 'text', None)            # fallback
            or ""
        )
        return content, choice.finish_reason

    def _call_model(model, max_tokens):
        """Make a single API call and return (content, finish_reason)."""
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )
        return _extract_content(response)

    for attempt in range(3):
        try:
            content, finish_reason = _call_model(PRIMARY_MODEL, 8192)

            # If finish_reason is length and content is empty,
            # the response was truncated at the token limit.
            # Increase max_tokens significantly.
            if finish_reason == "length" and not content.strip():
                console.print("[yellow]⚠ Response truncated at token limit "
                              "— retrying with max_tokens=32000[/yellow]")
                content, finish_reason = _call_model(PRIMARY_MODEL, 32000)

            if content.strip():
                return content

        except openai.RateLimitError:
            console.print("[yellow]⚠ Rate limit on primary — trying fallback[/yellow]")
            try:
                content, finish_reason = _call_model(FALLBACK_MODEL, 8192)

                if finish_reason == "length" and not content.strip():
                    console.print("[yellow]⚠ Fallback also truncated "
                                  "— retrying with max_tokens=32000[/yellow]")
                    content, finish_reason = _call_model(FALLBACK_MODEL, 32000)

                if content.strip():
                    return content
            except Exception as e:
                console.print(f"[red]✗ Fallback also failed: {e}[/red]")
        except Exception as e:
            console.print(f"[dim]Generation attempt {attempt+1} error: {e}[/dim]")
            time.sleep(1)
    return ""

# Startup message
console.print("[green]✓ LLM ready: Hy3 (primary) + Ling-2.6-1T (fallback)[/green]")

#!/usr/bin/env python3
"""
openrouter_lookup.py

Usage:
    openrouter_lookup.py "search term to summarize"

Requires:
    - OPENROUTER_API_KEY environment variable
    - requests (pip install requests)
    - Optional: Ollama CLI with a small model (defaults to OLLAMA_FORMAT_MODEL env)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
import requests

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(query: str) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    model = os.environ.get("OPENROUTER_MODEL", "google/gemma-7b-it")
    summary_model = os.environ.get("OPENROUTER_SUMMARY_MODEL", model)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://openrouter.ai",
        "Content-Type": "application/json",
    }
    payload = {
        "model": summary_model,
        "messages": [
            {"role": "system", "content": "You are a concise research assistant."},
            {
                "role": "user",
                "content": f"Give me a short summary and key facts for: {query}",
            },
        ],
    }

    response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected OpenRouter response: {json.dumps(data, indent=2)}")


def format_with_ollama(text: str) -> str:
    ollama_bin = shutil.which("ollama")
    if not ollama_bin:
        return textwrap.fill(text, width=88)

    model = os.environ.get("OLLAMA_FORMAT_MODEL", "llama3.2")
    prompt = (
        "Format the following summary into a concise bullet list with bold keywords.\n"
        "Keep it under 8 bullets.\n\n"
        f"{text}\n"
    )
    try:
        proc = subprocess.run(
            [ollama_bin, "run", model],
            text=True,
            input=prompt,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except FileNotFoundError:
        pass

    return textwrap.fill(text, width=88)


def main() -> None:
    parser = argparse.ArgumentParser(description="Query OpenRouter free models and format via Ollama.")
    parser.add_argument("query", help="Search term or question to summarize.")
    args = parser.parse_args()

    try:
        summary = call_openrouter(args.query)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error querying OpenRouter: {exc}", file=sys.stderr)
        sys.exit(1)

    formatted = format_with_ollama(summary)
    print(formatted)


if __name__ == "__main__":
    main()

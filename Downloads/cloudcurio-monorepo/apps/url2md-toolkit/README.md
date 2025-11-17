# URL → Markdown Toolkit (OpenRouter + LangChain/LangGraph)

This bundle is the skeleton for your URL-to-Markdown tool.

**Important:** The *real* script contents live in the ChatGPT code canvas.
Copy `url_to_markdown_openrouter.py` from the canvas and overwrite the
placeholder file in this folder.

Files in this zip:

- `url_to_markdown_openrouter.py` — main script (replace with canvas version)
- `requirements.txt` — suggested Python dependencies

Basic usage (after you replace the script with the canvas version):

```bash
pip install -r requirements.txt

export OPENROUTER_API_KEY="sk-or-..."

python url_to_markdown_openrouter.py "https://example.com/some/article"
```

You can also use:

```bash
python url_to_markdown_openrouter.py --urls-file urls.txt --download-images
```

Integrations:

- Optional observability via Langfuse & LangSmith (auto-detected if installed)
- LangChain `@tool` wrapper
- LangGraph `StateGraph` helper

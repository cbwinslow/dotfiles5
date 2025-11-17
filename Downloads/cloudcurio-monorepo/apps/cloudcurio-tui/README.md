# cloudcurio-tui

Terminal UI dashboard for your CloudCurio mono-repo constellation.

## Features

- Repo list from `CC_ROOT`
- Main markdown viewer (PROJECT_SUMMARY, RULES, AGENTS, etc.)
- AI sidebar (OpenAI or OpenRouter)
- Repo validator for required docs
- Layout profiles: default / infra / agents
- Command palette (`:`)
- Optional SSH mode via Charmbracelet Wish

## Quickstart

```bash
git clone <this repo> cloudcurio-tui
cd cloudcurio-tui

go mod init cloudcurio-tui
go get github.com/charmbracelet/bubbletea@latest
go get github.com/charmbracelet/bubbles@latest
go get github.com/charmbracelet/lipgloss@latest
go get github.com/charmbracelet/glamour@latest
go get github.com/charmbracelet/wish@latest
go get github.com/charmbracelet/wish/bubbletea@latest
go get github.com/charmbracelet/wish/logging@latest
go get github.com/gliderlabs/ssh@latest

export CC_ROOT="$HOME/dev/cloudcurio"
# Optional AI:
# export OPENAI_API_KEY="sk-..."
# export OPENROUTER_API_KEY="..."
# export OPENROUTER_MODEL="openrouter/auto"

go run .
```

## SSH Mode

```bash
export CC_TUI_SSH_SERVER=1
export CC_TUI_SSH_ADDR=":23234"               # optional
export CC_TUI_SSH_KEY="$HOME/.ssh/cloudcurio_tui"  # optional, auto-created path

go run .
# Then from another machine:
#   ssh -p 23234 user@host
```


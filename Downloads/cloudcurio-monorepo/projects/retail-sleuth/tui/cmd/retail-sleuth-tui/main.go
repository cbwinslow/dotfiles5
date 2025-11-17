package main

import (
    "log"
    "os"

    tea "github.com/charmbracelet/bubbletea"
)

type model struct {
    status string
}

func initialModel() model {
    return model{
        status: "Retail Sleuth TUI – press q to quit",
    }
}

func (m model) Init() tea.Cmd {
    return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "q", "ctrl+c":
            return m, tea.Quit
        }
    }
    return m, nil
}

func (m model) View() string {
    return m.status + "\n"
}

func main() {
    p := tea.NewProgram(initialModel())
    if err := p.Start(); err != nil {
        log.Println("Error running program:", err)
        os.Exit(1)
    }
}

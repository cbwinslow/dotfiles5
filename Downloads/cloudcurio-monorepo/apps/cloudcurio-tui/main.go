// ============================================================================
// File:        main.go
// Project:     cloudcurio-tui
// Author:      CBW + ChatGPT
// Date:        2025-11-16
//
// Summary:
//   Reusable TUI dashboard for managing the CloudCurio repo ecosystem.
//   - Left pane: repo list (scans CC_ROOT for repos)
//   - Center pane: rendered project docs (PROJECT_SUMMARY.md, RULES.md, etc.)
//   - Right pane: AI sidebar (chat pane + input), wired to OpenAI/OpenRouter via env vars.
//   - Includes project validator to ensure required docs exist per repo.
//   - Provides hotkeys to switch docs, validate repos, and query AI.
//   - Supports layout profiles (default/infra/agents) and a simple command palette.
//   - Can run as a local TUI or as an SSH app via Charmbracelet Wish.
//
// Inputs / Configuration:
//   Environment variables:
//     CC_ROOT              - root directory for CloudCurio repos (default: ~/dev/cloudcurio)
//     CC_THEME             - (optional) theme hint, e.g. "dark", "light" (not strictly used yet)
//     OPENAI_API_KEY       - (optional) if set, use OpenAI Chat Completions API
//     OPENAI_MODEL         - (optional) OpenAI model name (default: gpt-4.1-mini)
//     OPENROUTER_API_KEY   - (optional) if set and OPENAI_API_KEY not set, use OpenRouter
//     OPENROUTER_MODEL     - (optional) OpenRouter model (default: openrouter/auto)
//     CC_TUI_SSH_SERVER    - if "1", run as SSH server instead of local TUI
//     CC_TUI_SSH_ADDR      - SSH listen address (default ":23234")
//     CC_TUI_SSH_KEY       - SSH host key path (default: ~/.ssh/cloudcurio_tui)
//
// Outputs:
//   - Interactive terminal UI using Bubble Tea.
//   - AI answers rendered in the AI pane when configured.
//   - Validation report rendered in main pane.
//   - Optional SSH app entrypoint powered by Wish.
//
// Keybindings:
//   Global:
//     Up/Down            : Navigate repo list
//     Enter              : In repos pane, load PROJECT_SUMMARY.md
//                          In AI pane, submit prompt to LLM
//     Tab                : Cycle active pane (Repos -> Main -> AI -> ...)
//     a                  : Toggle AI sidebar (show/hide)
//     v                  : Validate all repos (required doc set)
//     :                  : Open command palette (e.g. "validate", "open RULES", "layout infra")
//     1                  : Layout profile: default (all repos)
//     2                  : Layout profile: infra-focused
//     3                  : Layout profile: agents-focused
//     q / Ctrl+C         : Quit TUI
//
//   Repo doc shortcuts (when a repo is selected):
//     s                  : Show PROJECT_SUMMARY.md
//     r                  : Show RULES.md
//     g                  : Show AGENTS.md
//     i                  : Show INSTRUCTIONS.md
//     j                  : Show JOURNAL.md
//     k                  : Show SRS.md
//     t                  : Show TASKS.md
//     y                  : Show TESTING.md
//
// Modification Log:
//   2025-11-15 - Initial scaffold with pane layout and markdown render.
//   2025-11-16 - Added AI sidebar wiring (OpenAI/OpenRouter),
//                validation command, doc hotkeys, layout profiles,
//                command palette, and Wish-based SSH server mode.
// ============================================================================

package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "os"
    "path/filepath"
    "strings"
    "time"

    tea "github.com/charmbracelet/bubbletea"
    "github.com/charmbracelet/bubbles/list"
    "github.com/charmbracelet/bubbles/textinput"
    "github.com/charmbracelet/bubbles/viewport"
    "github.com/charmbracelet/glamour"
    "github.com/charmbracelet/lipgloss"
    bm "github.com/charmbracelet/wish/bubbletea"
    wlog "github.com/charmbracelet/wish/logging"
    "github.com/charmbracelet/wish"
    "github.com/gliderlabs/ssh"
)

// ---------------------------------------------------------------------
// Types & Constants
// ---------------------------------------------------------------------

type pane int

const (
    paneRepos pane = iota
    paneMain
    paneAI
)

// layoutProfile controls repo filtering / emphasis in the UI.
type layoutProfile int

const (
    profileDefault layoutProfile = iota
    profileInfra
    profileAgents
)

// repoItem is an item for the repo list pane.
type repoItem struct {
    name string
    path string
}

func (r repoItem) Title() string       { return r.name }
func (r repoItem) Description() string { return r.path }
func (r repoItem) FilterValue() string { return r.name }

// aiResponseMsg carries the result of an AI call back into the TUI.
type aiResponseMsg struct {
    response string
    err      error
}

// ---------------------------------------------------------------------
// Model
// ---------------------------------------------------------------------

type model struct {
    width      int
    height     int
    ready      bool
    ccRoot     string
    activePane pane
    showAIPane bool

    statusMsg   string
    statusError string

    repos    list.Model
    allRepos []list.Item

    mainView viewport.Model
    aiView   viewport.Model
    aiInput  textinput.Model

    // Command palette
    commandMode  bool
    commandInput textinput.Model

    mdRenderer *glamour.TermRenderer

    // Styles
    repoStyle   lipgloss.Style
    mainStyle   lipgloss.Style
    aiStyle     lipgloss.Style
    statusStyle lipgloss.Style
    errorStyle  lipgloss.Style

    // Flags
    aiLoading  bool
    validating bool

    // Layout
    profile layoutProfile

    // Required docs for validation
    requiredDocs []string
}

// ---------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------

func initialModel(ccRoot string) model {
    items := scanRepos(ccRoot)

    repoList := list.New(items, list.NewDefaultDelegate(), 0, 0)
    repoList.SetFilteringEnabled(true)
    repoList.Title = "Repositories"

    mainVP := viewport.New(0, 0)
    mainVP.SetContent("Select a repo and press Enter or 's' to load PROJECT_SUMMARY.md")

    aiVP := viewport.New(0, 0)
    aiVP.SetContent("AI Chat Pane

Type in the input below and press Enter.
Configure OPENAI_API_KEY or OPENROUTER_API_KEY to enable real responses.")

    aiInput := textinput.New()
    aiInput.Placeholder = "Ask an AI agent something about your project…"
    aiInput.CharLimit = 500
    aiInput.Prompt = "> "

    cmdInput := textinput.New()
    cmdInput.Placeholder = "Command (validate, open RULES, layout infra)..."
    cmdInput.CharLimit = 200
    cmdInput.Prompt = ": "

    mdRend, err := glamour.NewTermRenderer(
        glamour.WithAutoStyle(),
        glamour.WithWordWrap(80),
    )
    if err != nil {
        mdRend = nil
    }

    repoStyle := lipgloss.NewStyle().
        Border(lipgloss.RoundedBorder()).
        BorderForeground(lipgloss.Color("63")).
        Padding(0, 1)

    mainStyle := lipgloss.NewStyle().
        Border(lipgloss.RoundedBorder()).
        BorderForeground(lipgloss.Color("39")).
        Padding(0, 1)

    aiStyle := lipgloss.NewStyle().
        Border(lipgloss.RoundedBorder()).
        BorderForeground(lipgloss.Color("205")).
        Padding(0, 1)

    statusStyle := lipgloss.NewStyle().
        Foreground(lipgloss.Color("241")).
        PaddingLeft(1)

    errorStyle := lipgloss.NewStyle().
        Foreground(lipgloss.Color("196")).
        Bold(true).
        PaddingLeft(1)

    required := []string{
        "PROJECT_SUMMARY.md",
        "RULES.md",
        "AGENTS.md",
        "INSTRUCTIONS.md",
        "JOURNAL.md",
        "SRS.md",
        "TASKS.md",
        "TESTING.md",
    }

    return model{
        ccRoot:        ccRoot,
        activePane:    paneRepos,
        showAIPane:    true,
        statusMsg:     fmt.Sprintf("CC_ROOT: %s", ccRoot),
        repos:         repoList,
        allRepos:      items,
        mainView:      mainVP,
        aiView:        aiVP,
        aiInput:       aiInput,
        commandMode:   false,
        commandInput:  cmdInput,
        mdRenderer:    mdRend,
        repoStyle:     repoStyle,
        mainStyle:     mainStyle,
        aiStyle:       aiStyle,
        statusStyle:   statusStyle,
        errorStyle:    errorStyle,
        aiLoading:     false,
        validating:    false,
        profile:       profileDefault,
        requiredDocs:  required,
    }
}

// scanRepos looks for directories in ccRoot and creates repo list items.
func scanRepos(ccRoot string) []list.Item {
    entries, err := os.ReadDir(ccRoot)
    if err != nil {
        log.Printf("[cloudcurio-tui] warning: unable to read CC_ROOT (%s): %v", ccRoot, err)
        return []list.Item{}
    }

    var items []list.Item
    for _, e := range entries {
        if !e.IsDir() {
            continue
        }
        name := e.Name()
        path := filepath.Join(ccRoot, name)
        items = append(items, repoItem{name: name, path: path})
    }
    return items
}

// ---------------------------------------------------------------------
// Bubble Tea Implementation
// ---------------------------------------------------------------------

func (m model) Init() tea.Cmd {
    return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    var cmds []tea.Cmd

    switch msg := msg.(type) {
    case tea.WindowSizeMsg:
        m.width = msg.Width
        m.height = msg.Height
        m.ready = true
        m = m.resizePanes()
        return m, nil

    case aiResponseMsg:
        m.aiLoading = false
        if msg.err != nil {
            m.statusError = fmt.Sprintf("AI error: %v", msg.err)
            m.appendAI("[error] " + msg.err.Error())
        } else {
            m.statusError = ""
            m.appendAI("AI: " + msg.response)
        }
        return m, nil

    case tea.KeyMsg:
        // Command palette has priority when active.
        if m.commandMode {
            sw := msg.String()
            switch sw {
            case "enter":
                cmdStr := strings.TrimSpace(m.commandInput.Value())
                m.commandMode = false
                m.commandInput.Blur()
                m.commandInput.SetValue("")
                m = m.executeCommand(cmdStr)
                return m, nil
            case "esc":
                m.commandMode = false
                m.commandInput.Blur()
                m.statusMsg = "Command cancelled"
                return m, nil
            default:
                var c tea.Cmd
                m.commandInput, c = m.commandInput.Update(msg)
                return m, c
            }
        }

        switch msg.String() {
        case "ctrl+c", "q":
            return m, tea.Quit

        case "tab":
            m.activePane = (m.activePane + 1) % 3

        case "a":
            m.showAIPane = !m.showAIPane
            m = m.resizePanes()

        case "v":
            m.validating = true
            report := m.validateRepos()
            m.mainView.SetContent(report)
            m.mainView.GotoTop()
            m.validating = false
            m.statusMsg = "Validation complete."

        case ":":
            m.commandMode = true
            m.commandInput.SetValue("")
            m.commandInput.Focus()
            m.statusMsg = "Command mode: type and press Enter"
            return m, nil

        case "1":
            m.profile = profileDefault
            m = m.applyProfileFilter()
            m.statusMsg = "Layout: default"

        case "2":
            m.profile = profileInfra
            m = m.applyProfileFilter()
            m.statusMsg = "Layout: infra"

        case "3":
            m.profile = profileAgents
            m = m.applyProfileFilter()
            m.statusMsg = "Layout: agents"

        case "enter":
            switch m.activePane {
            case paneRepos:
                m = m.loadSelectedRepoFile("PROJECT_SUMMARY.md")
            case paneAI:
                if !m.aiLoading {
                    m, cmds = m.handleAISubmit(cmds)
                }
            }

        // Repo doc shortcuts
        case "s":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("PROJECT_SUMMARY.md")
            }
        case "r":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("RULES.md")
            }
        case "g":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("AGENTS.md")
            }
        case "i":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("INSTRUCTIONS.md")
            }
        case "j":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("JOURNAL.md")
            }
        case "k":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("SRS.md")
            }
        case "t":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("TASKS.md")
            }
        case "y":
            if m.activePane == paneRepos || m.activePane == paneMain {
                m = m.loadSelectedRepoFile("TESTING.md")
            }
        }
    }

    // Route messages to active pane components.
    switch m.activePane {
    case paneRepos:
        var cmd tea.Cmd
        m.repos, cmd = m.repos.Update(msg)
        cmds = append(cmds, cmd)

    case paneMain:
        var cmd tea.Cmd
        m.mainView, cmd = m.mainView.Update(msg)
        cmds = append(cmds, cmd)

    case paneAI:
        var cmd tea.Cmd
        m.aiInput, cmd = m.aiInput.Update(msg)
        cmds = append(cmds, cmd)

        m.aiView, cmd = m.aiView.Update(msg)
        cmds = append(cmds, cmd)
    }

    return m, tea.Batch(cmds...)
}

func (m model) View() string {
    if !m.ready {
        return "Loading CloudCurio TUI...
"
    }

    repoView := m.repoStyle.Render(m.repos.View())
    mainView := m.mainStyle.Render(m.mainView.View())

    var aiSection string
    if m.showAIPane {
        aiCombined := m.aiView.View() + "
" + m.aiInput.View()
        if m.aiLoading {
            aiCombined += "
[waiting for AI response...]"
        }
        aiSection = m.aiStyle.Render(aiCombined)
    }

    var layout string
    if m.showAIPane {
        layout = lipgloss.JoinHorizontal(lipgloss.Top, repoView, mainView, aiSection)
    } else {
        layout = lipgloss.JoinHorizontal(lipgloss.Top, repoView, mainView)
    }

    // Status line
    active := m.activePaneLabel()
    profile := m.profileLabel()
    statusLeft := fmt.Sprintf(
        "Active: %s | Layout: %s | a: toggle AI | tab: switch pane | v: validate | : command | 1/2/3: layouts | q: quit",
        active,
        profile,
    )

    statusText := statusLeft
    if m.statusMsg != "" {
        statusText += "  | " + m.statusMsg
    }

    status := m.statusStyle.Render(statusText)
    if m.statusError != "" {
        status += "  " + m.errorStyle.Render(m.statusError)
    }

    footer := status
    if m.commandMode {
        footer = m.commandInput.View() + "
" + status
    }

    return lipgloss.JoinVertical(lipgloss.Left, layout, footer)
}

// resizePanes recalculates pane sizes when window or AI toggle changes.
func (m model) resizePanes() model {
    if m.width <= 0 || m.height <= 0 {
        return m
    }

    height := m.height - 1
    if height < 5 {
        height = m.height
    }

    var repoWidth, mainWidth, aiWidth int
    if m.showAIPane {
        repoWidth = int(float64(m.width) * 0.2)
        aiWidth = int(float64(m.width) * 0.25)
        mainWidth = m.width - repoWidth - aiWidth
    } else {
        repoWidth = int(float64(m.width) * 0.25)
        mainWidth = m.width - repoWidth
        aiWidth = 0
    }

    if repoWidth < 20 {
        repoWidth = 20
    }
    if mainWidth < 20 {
        mainWidth = 20
    }

    m.repos.SetSize(repoWidth-4, height-2)
    m.mainView.Width = mainWidth - 4
    m.mainView.Height = height - 2

    if m.showAIPane {
        m.aiView.Width = aiWidth - 4
        m.aiView.Height = height - 4
    } else {
        m.aiView.Width = 0
        m.aiView.Height = 0
    }

    return m
}

func (m model) activePaneLabel() string {
    switch m.activePane {
    case paneRepos:
        return "Repos"
    case paneMain:
        return "Main"
    case paneAI:
        return "AI"
    default:
        return "Unknown"
    }
}

func (m model) profileLabel() string {
    switch m.profile {
    case profileDefault:
        return "default"
    case profileInfra:
        return "infra"
    case profileAgents:
        return "agents"
    default:
        return "unknown"
    }
}

// applyProfileFilter filters the repo list based on the active layout profile.
func (m model) applyProfileFilter() model {
    if len(m.allRepos) == 0 {
        return m
    }

    var filtered []list.Item

    switch m.profile {
    case profileInfra:
        for _, it := range m.allRepos {
            if r, ok := it.(repoItem); ok {
                name := strings.ToLower(r.name)
                if strings.Contains(name, "infra") || strings.Contains(name, "cloudcurio-infra") {
                    filtered = append(filtered, it)
                }
            }
        }
    case profileAgents:
        for _, it := range m.allRepos {
            if r, ok := it.(repoItem); ok {
                name := strings.ToLower(r.name)
                if strings.Contains(name, "agent") || strings.Contains(name, "agents") {
                    filtered = append(filtered, it)
                }
            }
        }
    default:
        filtered = m.allRepos
    }

    // Fallback: if filter produced no results, show all.
    if len(filtered) == 0 {
        filtered = m.allRepos
    }

    m.repos.SetItems(filtered)
    return m
}

// loadSelectedRepoFile reads the given filename for the selected repo and
// renders it into the main viewport.
func (m model) loadSelectedRepoFile(filename string) model {
    item, ok := m.repos.SelectedItem().(repoItem)
    if !ok {
        m.statusError = "No repo selected"
        return m
    }

    targetPath := filepath.Join(item.path, filename)
    data, err := os.ReadFile(targetPath)
    if err != nil {
        m.mainView.SetContent(fmt.Sprintf("Error reading %s:
%v", targetPath, err))
        m.statusError = fmt.Sprintf("Failed to load %s", filename)
        return m
    }

    content := string(data)
    if m.mdRenderer != nil && strings.HasSuffix(strings.ToLower(filename), ".md") {
        if rendered, err := m.mdRenderer.Render(content); err == nil {
            content = rendered
        }
    }

    m.mainView.SetContent(content)
    m.mainView.GotoTop()
    m.statusMsg = fmt.Sprintf("Loaded %s", targetPath)
    m.statusError = ""
    return m
}

// appendAI appends a line to the AI viewport.
func (m *model) appendAI(line string) {
    current := m.aiView.View()
    if strings.TrimSpace(current) == "" {
        m.aiView.SetContent(line)
    } else {
        m.aiView.SetContent(current + "
" + line)
    }
    m.aiView.GotoBottom()
}

// handleAISubmit collects the prompt, appends it to the AI view, and triggers
// an async AI call via tea.Cmd.
func (m model) handleAISubmit(cmds []tea.Cmd) (model, []tea.Cmd) {
    prompt := strings.TrimSpace(m.aiInput.Value())
    if prompt == "" {
        return m, cmds
    }

    item, _ := m.repos.SelectedItem().(repoItem)
    repoName := item.name

    m.appendAI("You: " + prompt)
    m.aiInput.SetValue("")
    m.aiLoading = true
    m.statusMsg = "Sending prompt to AI backend..."

    cmd := aiRequestCmd(prompt, repoName, m.ccRoot)
    cmds = append(cmds, cmd)

    return m, cmds
}

// executeCommand runs a command from the command palette.
func (m model) executeCommand(cmdStr string) model {
    if cmdStr == "" {
        return m
    }

    lower := strings.ToLower(cmdStr)

    switch {
    case lower == "validate":
        m.validating = true
        report := m.validateRepos()
        m.mainView.SetContent(report)
        m.mainView.GotoTop()
        m.validating = false
        m.statusMsg = "Validation complete via command."

    case strings.HasPrefix(lower, "open "):
        arg := strings.TrimSpace(cmdStr[5:])
        filename := mapDocAliasToFilename(arg)
        if filename == "" {
            m.statusError = "Unknown doc alias: " + arg
            return m
        }
        m = m.loadSelectedRepoFile(filename)

    case strings.HasPrefix(lower, "layout "):
        arg := strings.TrimSpace(lower[7:])
        switch arg {
        case "default":
            m.profile = profileDefault
        case "infra":
            m.profile = profileInfra
        case "agents":
            m.profile = profileAgents
        default:
            m.statusError = "Unknown layout: " + arg
            return m
        }
        m = m.applyProfileFilter()
        m.statusMsg = "Layout changed via command."

    default:
        m.statusError = "Unknown command: " + cmdStr
    }

    return m
}

// mapDocAliasToFilename maps simple aliases to actual doc filenames.
func mapDocAliasToFilename(alias string) string {
    alias = strings.ToLower(strings.TrimSpace(alias))
    switch alias {
    case "summary", "project", "project_summary", "s":
        return "PROJECT_SUMMARY.md"
    case "rules", "r":
        return "RULES.md"
    case "agents", "g":
        return "AGENTS.md"
    case "instructions", "i":
        return "INSTRUCTIONS.md"
    case "journal", "j":
        return "JOURNAL.md"
    case "srs", "k":
        return "SRS.md"
    case "tasks", "t":
        return "TASKS.md"
    case "testing", "test", "y":
        return "TESTING.md"
    default:
        return ""
    }
}

// validateRepos checks each repo for the required docs and returns a report.
func (m model) validateRepos() string {
    var b strings.Builder
    b.WriteString("CloudCurio Repo Validation Report
")
    b.WriteString(time.Now().Format(time.RFC3339) + "

")

    items := m.allRepos
    if len(items) == 0 {
        b.WriteString("No repositories found under CC_ROOT.
")
        return b.String()
    }

    for _, it := range items {
        repo, ok := it.(repoItem)
        if !ok {
            continue
        }
        b.WriteString(fmt.Sprintf("Repo: %s
", repo.name))

        missing := []string{}
        for _, doc := range m.requiredDocs {
            p := filepath.Join(repo.path, doc)
            if _, err := os.Stat(p); err != nil {
                missing = append(missing, doc)
            }
        }

        if len(missing) == 0 {
            b.WriteString("  ✓ All required docs present.

")
        } else {
            b.WriteString("  ✗ Missing docs:
")
            for _, doc := range missing {
                b.WriteString("    - " + doc + "
")
            }
            b.WriteString("
")
        }
    }

    return b.String()
}

// ---------------------------------------------------------------------
// AI Backend Integration
// ---------------------------------------------------------------------

// aiRequestCmd returns a tea.Cmd that calls an AI backend asynchronously.
func aiRequestCmd(prompt, repoName, ccRoot string) tea.Cmd {
    return func() tea.Msg {
        ctx := fmt.Sprintf("Repo: %s
CC_ROOT: %s", repoName, ccRoot)
        resp, err := callAIBackend(prompt, ctx)
        return aiResponseMsg{response: resp, err: err}
    }
}

// callAIBackend chooses between OpenAI and OpenRouter based on env vars.
func callAIBackend(prompt, context string) (string, error) {
    if key := os.Getenv("OPENAI_API_KEY"); key != "" {
        model := os.Getenv("OPENAI_MODEL")
        if model == "" {
            model = "gpt-4.1-mini"
        }
        return callOpenAIChat(key, model, prompt, context)
    }

    if key := os.Getenv("OPENROUTER_API_KEY"); key != "" {
        model := os.Getenv("OPENROUTER_MODEL")
        if model == "" {
            model = "openrouter/auto"
        }
        return callOpenRouterChat(key, model, prompt, context)
    }

    return "", fmt.Errorf("no AI backend configured (set OPENAI_API_KEY or OPENROUTER_API_KEY)")
}

// Minimal structs for OpenAI / OpenRouter chat API calls.

type openAIChatMessage struct {
    Role    string `json:"role"`
    Content string `json:"content"`
}

type openAIChatRequest struct {
    Model    string              `json:"model"`
    Messages []openAIChatMessage `json:"messages"`
}

type openAIChatChoice struct {
    Message openAIChatMessage `json:"message"`
}

type openAIChatResponse struct {
    Choices []openAIChatChoice `json:"choices"`
}

// callOpenAIChat sends a chat completion request to OpenAI.
func callOpenAIChat(apiKey, model, prompt, context string) (string, error) {
    body := openAIChatRequest{
        Model: model,
        Messages: []openAIChatMessage{
            {Role: "system", Content: "You are a helpful assistant for the CloudCurio project. Use the provided repo context when helpful."},
            {Role: "user", Content: fmt.Sprintf("Context:
%s", context)},
            {Role: "user", Content: prompt},
        },
    }

    data, err := json.Marshal(body)
    if err != nil {
        return "", err
    }

    req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(data))
    if err != nil {
        return "", err
    }
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+apiKey)

    client := &http.Client{Timeout: 60 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 300 {
        b, _ := io.ReadAll(resp.Body)
        return "", fmt.Errorf("openai api error: %s", string(b))
    }

    var parsed openAIChatResponse
    if err := json.NewDecoder(resp.Body).Decode(&parsed); err != nil {
        return "", err
    }
    if len(parsed.Choices) == 0 {
        return "", fmt.Errorf("no choices returned from OpenAI")
    }

    return parsed.Choices[0].Message.Content, nil
}

// OpenRouter is API-compatible with OpenAI's chat/completions in many setups.

type openRouterChatRequest openAIChatRequest

type openRouterChatResponse openAIChatResponse

func callOpenRouterChat(apiKey, model, prompt, context string) (string, error) {
    body := openRouterChatRequest{
        Model: model,
        Messages: []openAIChatMessage{
            {Role: "system", Content: "You are a helpful assistant for the CloudCurio project. Use the provided repo context when helpful."},
            {Role: "user", Content: fmt.Sprintf("Context:
%s", context)},
            {Role: "user", Content: prompt},
        },
    }

    data, err := json.Marshal(body)
    if err != nil {
        return "", err
    }

    req, err := http.NewRequest("POST", "https://openrouter.ai/api/v1/chat/completions", bytes.NewBuffer(data))
    if err != nil {
        return "", err
    }
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+apiKey)
    req.Header.Set("HTTP-Referer", "https://cloudcurio.cc")
    req.Header.Set("X-Title", "CloudCurio TUI")

    client := &http.Client{Timeout: 60 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 300 {
        b, _ := io.ReadAll(resp.Body)
        return "", fmt.Errorf("openrouter api error: %s", string(b))
    }

    var parsed openRouterChatResponse
    if err := json.NewDecoder(resp.Body).Decode(&parsed); err != nil {
        return "", err
    }
    if len(parsed.Choices) == 0 {
        return "", fmt.Errorf("no choices returned from OpenRouter")
    }

    return parsed.Choices[0].Message.Content, nil
}

// ---------------------------------------------------------------------
// SSH Server Mode (Wish)
// ---------------------------------------------------------------------

// runSSHServer starts a Wish-based SSH server that serves the TUI.
func runSSHServer(ccRoot string) error {
    addr := os.Getenv("CC_TUI_SSH_ADDR")
    if addr == "" {
        addr = ":23234"
    }

    keyPath := os.Getenv("CC_TUI_SSH_KEY")
    if keyPath == "" {
        home, err := os.UserHomeDir()
        if err != nil {
            return fmt.Errorf("could not determine home directory: %w", err)
        }
        keyPath = filepath.Join(home, ".ssh", "cloudcurio_tui")
    }

    server, err := wish.NewServer(
        wish.WithAddress(addr),
        wish.WithHostKeyPath(keyPath),
        wish.WithMiddleware(
            bm.Middleware(func(s ssh.Session) (tea.Model, []tea.ProgramOption) {
                m := initialModel(ccRoot)
                return m, []tea.ProgramOption{tea.WithAltScreen()}
            }),
            wlog.Middleware(),
        ),
    )
    if err != nil {
        return fmt.Errorf("failed to create SSH server: %w", err)
    }

    log.Printf("[cloudcurio-tui] SSH server listening on %s (host key: %s)", addr, keyPath)
    return server.ListenAndServe()
}

// ---------------------------------------------------------------------
// main()
// ---------------------------------------------------------------------

func main() {
    log.SetOutput(os.Stderr)

    ccRoot := os.Getenv("CC_ROOT")
    if ccRoot == "" {
        home, err := os.UserHomeDir()
        if err != nil {
            log.Fatalf("could not determine home directory: %v", err)
        }
        ccRoot = filepath.Join(home, "dev", "cloudcurio")
    }

    if _, err := os.Stat(ccRoot); os.IsNotExist(err) {
        log.Printf("[cloudcurio-tui] warning: CC_ROOT does not exist yet: %s", ccRoot)
        log.Printf("Create it with your cc_boot.sh script or adjust CC_ROOT.")
    }

    if os.Getenv("CC_TUI_SSH_SERVER") == "1" {
        if err := runSSHServer(ccRoot); err != nil {
            log.Fatalf("error running SSH server: %v", err)
        }
        return
    }

    m := initialModel(ccRoot)

    p := tea.NewProgram(m, tea.WithAltScreen())
    if _, err := p.Run(); err != nil {
        log.Fatalf("error running TUI: %v", err)
    }
}

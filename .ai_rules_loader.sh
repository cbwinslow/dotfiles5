#!/bin/bash
# =============================================================================
# AI AGENT RULES LOADER - Universal Rules Enforcement System
# =============================================================================
# This script automatically loads and enforces AI agent rules for all AI systems
# in the cbwinslow environment. It provides a centralized mechanism for rule
# distribution and compliance monitoring.

# =============================================================================
# CONFIGURATION
# =============================================================================

# Paths
AI_RULES_FILE="${HOME}/.ai_agent_rules"
AI_RULES_LOADER_VERSION="2.0.0"
AI_RULES_CACHE_DIR="${HOME}/.cache/ai_rules"
AI_RULES_LOG="${HOME}/logs/ai_rules_enforcement.log"

# Ensure directories exist
mkdir -p "$(dirname "$AI_RULES_LOG")"
mkdir -p "$AI_RULES_CACHE_DIR"

# Agent detection patterns
AGENT_PATTERNS=(
    "opencode"
    "cursor"
    "claude"
    "chatgpt"
    "copilot"
    "codeium"
    "tabnine"
    "continue"
    "codegpt"
    "codex"
    "cline"
    "junie"
    "aider"
    "cursor"
    "supermaven"
)

# =============================================================================
# RULES LOADING FUNCTIONS
# =============================================================================

# Load core AI rules
load_ai_rules() {
    local agent_name="${1:-unknown}"
    local session_id="${2:-$(date +%s)}"
    
    # Create log entry
    local log_entry="[$(date '+%Y-%m-%d %H:%M:%S')] AI Rules Loader v$AI_RULES_LOADER_VERSION"
    log_entry+=" | Agent: $agent_name"
    log_entry+=" | Session: $session_id"
    
    # Check if rules file exists
    if [[ ! -f "$AI_RULES_FILE" ]]; then
        echo "❌ CRITICAL: AI rules file not found at $AI_RULES_FILE" | tee -a "$AI_RULES_LOG"
        echo "$log_entry | ERROR: Rules file missing" >> "$AI_RULES_LOG"
        return 1
    fi
    
    # Source the rules file
    source "$AI_RULES_FILE"
    
    # Set environment variables for agent
    export AI_RULES_ACTIVE=true
    export AI_RULES_VERSION="$AI_RULES_LOADER_VERSION"
    export AI_AGENT_NAME="$agent_name"
    export AI_SESSION_ID="$session_id"
    export AI_RULES_LOADED_TIME="$(date '+%Y-%m-%d %H:%M:%S')"
    
    # Log successful loading
    echo "$log_entry | SUCCESS: Rules loaded and active" >> "$AI_RULES_LOG"
    
    return 0
}

# Detect AI agent environment
detect_ai_agent() {
    local detected_agents=()
    
    # Check environment variables
    if [[ -n "$TERM_PROGRAM" ]]; then
        case "$TERM_PROGRAM" in
            "vscode"|"vscode-insiders") detected_agents+=("vscode") ;;
            "cursor") detected_agents+=("cursor") ;;
            "hyper") detected_agents+=("hyper") ;;
            "wezterm") detected_agents+=("wezterm") ;;
        esac
    fi
    
    # Check running processes
    if command -v pgrep >/dev/null 2>&1; then
        for pattern in "${AGENT_PATTERNS[@]}"; do
            if pgrep -i "$pattern" >/dev/null 2>&1; then
                detected_agents+=("$pattern")
            fi
        done
    fi
    
    # Check specific AI tool environments
    if [[ -n "$OPENAI_API_KEY" ]]; then detected_agents+=("openai"); fi
    if [[ -n "$ANTHROPIC_API_KEY" ]]; then detected_agents+=("anthropic"); fi
    if [[ -n "$OPENROUTER_API_KEY" ]]; then detected_agents+=("openrouter"); fi
    
    # Check for specific directories
    if [[ -d "$HOME/.cursor" ]]; then detected_agents+=("cursor"); fi
    if [[ -d "$HOME/.continue" ]]; then detected_agents+=("continue"); fi
    if [[ -d "$HOME/.cline" ]]; then detected_agents+=("cline"); fi
    
    # Remove duplicates and return
    printf '%s\n' "${detected_agents[@]}" | sort -u
}

# =============================================================================
# RULES ENFORCEMENT FUNCTIONS
# =============================================================================

# Validate command against AI rules
validate_ai_command() {
    local command="$1"
    local target_file="${2:-}"
    
    # Check if rules are loaded
    if [[ "$AI_RULES_ACTIVE" != "true" ]]; then
        echo "⚠️  AI rules not active - loading now..."
        load_ai_rules "shell_validation"
    fi
    
    # Use existing validation functions if available
    if declare -f ai_validate_operation >/dev/null 2>&1; then
        ai_validate_operation "$command" "$target_file"
        return $?
    fi
    
    # Fallback validation
    case "$command" in
        "rm"|"mv"|"chmod"|"chown")
            if [[ "$target_file" =~ (^/etc/|^/usr/|^/boot/|^/sys/) ]]; then
                echo "🚫 AI RULE VIOLATION: System file modification blocked"
                return 1
            fi
            ;;
        "ssh"|"scp"|"sftp")
            if [[ "$target_file" =~ (config|known_hosts|id_) ]]; then
                echo "🚫 AI RULE VIOLATION: SSH configuration modification blocked"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Hook into common commands for enforcement
create_command_hooks() {
    # Create wrapper functions for dangerous commands
    eval 'ai_safe_rm() {
        if validate_ai_command "rm" "$1"; then
            command rm "$@"
        else
            echo "❌ Command blocked by AI rules"
            return 1
        fi
    }'
    
    eval 'ai_safe_mv() {
        if validate_ai_command "mv" "$1"; then
            command mv "$@"
        else
            echo "❌ Command blocked by AI rules"
            return 1
        fi
    }'
    
    eval 'ai_safe_chmod() {
        if validate_ai_command "chmod" "$1"; then
            command chmod "$@"
        else
            echo "❌ Command blocked by AI rules"
            return 1
        fi
    }'
    
    # Replace dangerous commands with safe versions
    alias rm='ai_safe_rm'
    alias mv='ai_safe_mv'
    alias chmod='ai_safe_chmod'
}

# =============================================================================
# AGENT INTEGRATION FUNCTIONS
# =============================================================================

# Initialize rules for specific AI agent
initialize_agent_rules() {
    local agent_type="$1"
    local agent_config="$2"
    
    echo "🤖 Initializing AI rules for agent: $agent_type"
    
    # Load core rules
    if ! load_ai_rules "$agent_type"; then
        echo "❌ Failed to load AI rules for $agent_type"
        return 1
    fi
    
    # Load agent-specific rules if available
    local agent_rules_file="${HOME}/.ai_agent_rules.d/${agent_type}.rules"
    if [[ -f "$agent_rules_file" ]]; then
        echo "📋 Loading agent-specific rules from $agent_rules_file"
        source "$agent_rules_file"
    fi
    
    # Create command hooks for enforcement
    create_command_hooks
    
    # Display rules summary
    if declare -f ai_show_rules >/dev/null 2>&1; then
        ai_show_rules
    fi
    
    echo "✅ AI rules initialized for $agent_type"
    return 0
}

# Auto-load rules for detected agents
auto_load_rules() {
    local detected_agents=($(detect_ai_agent))
    
    if [[ ${#detected_agents[@]} -eq 0 ]]; then
        return 0
    fi
    
    echo ""
    echo "🤖 AI Agents Detected: ${detected_agents[*]}"
    echo "📋 Loading AI Agent Rules..."
    
    for agent in "${detected_agents[@]}"; do
        initialize_agent_rules "$agent"
    done
    
    echo ""
}

# =============================================================================
# COMPLIANCE MONITORING
# =============================================================================

# Check AI agent compliance
check_compliance() {
    local agent_name="${1:-current}"
    
    echo "🔍 Checking AI Agent Compliance for: $agent_name"
    
    # Check if rules are loaded
    if [[ "$AI_RULES_ACTIVE" != "true" ]]; then
        echo "❌ AI rules not active"
        return 1
    fi
    
    # Check core rule functions
    local required_functions=(
        "ai_validate_operation"
        "ai_check_ssh_safety"
        "ai_check_system_safety"
    )
    
    for func in "${required_functions[@]}"; do
        if ! declare -f "$func" >/dev/null 2>&1; then
            echo "⚠️  Missing required function: $func"
        fi
    done
    
    # Check environment variables
    local required_vars=(
        "AI_RULES_ACTIVE"
        "AI_RULES_VERSION"
        "AI_AGENT_NAME"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo "⚠️  Missing required variable: $var"
        fi
    done
    
    echo "✅ Compliance check completed"
    return 0
}

# Generate compliance report
generate_compliance_report() {
    local report_file="${AI_RULES_CACHE_DIR}/compliance_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "agent_name": "${AI_AGENT_NAME:-unknown}",
    "session_id": "${AI_SESSION_ID:-unknown}",
    "rules_version": "$AI_RULES_LOADER_VERSION",
    "rules_active": "$AI_RULES_ACTIVE",
    "compliance_status": "$(check_compliance >/dev/null 2>&1 && echo "compliant" || echo "non_compliant")",
    "environment": {
        "shell": "$SHELL",
        "user": "$USER",
        "home": "$HOME",
        "pwd": "$PWD"
    },
    "detected_agents": $(detect_ai_agent | jq -R . | jq -s .)
}
EOF
    
    echo "📊 Compliance report generated: $report_file"
    echo "$report_file"
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Show AI rules status
show_ai_rules_status() {
    echo "🤖 AI Agent Rules Status"
    echo "========================"
    echo "Rules Active: $AI_RULES_ACTIVE"
    echo "Rules Version: $AI_RULES_LOADER_VERSION"
    echo "Agent Name: ${AI_AGENT_NAME:-not_set}"
    echo "Session ID: ${AI_SESSION_ID:-not_set}"
    echo "Loaded Time: ${AI_RULES_LOADED_TIME:-not_set}"
    echo "Rules File: $AI_RULES_FILE"
    echo "Log File: $AI_RULES_LOG"
    echo ""
    
    if [[ "$AI_RULES_ACTIVE" == "true" ]]; then
        echo "✅ AI rules are currently active and enforced"
        echo "📋 Type 'ai_show_rules' to see detailed rules"
        echo "🔍 Type 'check_compliance' to verify compliance"
    else
        echo "❌ AI rules are not active"
        echo "🔄 Type 'load_ai_rules' to activate rules"
    fi
}

# Reload AI rules
reload_ai_rules() {
    echo "🔄 Reloading AI Agent Rules..."
    
    # Reset environment
    unset AI_RULES_ACTIVE AI_RULES_VERSION AI_AGENT_NAME AI_SESSION_ID AI_RULES_LOADED_TIME
    
    # Reload rules
    if load_ai_rules "${AI_AGENT_NAME:-reloaded}"; then
        echo "✅ AI rules reloaded successfully"
        return 0
    else
        echo "❌ Failed to reload AI rules"
        return 1
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

# Auto-load rules if AI agents are detected
if [[ "${AI_AUTO_LOAD_RULES:-true}" == "true" ]]; then
    auto_load_rules
fi

# Export functions for use in other scripts (zsh compatible)
functions[load_ai_rules]=1
functions[detect_ai_agent]=1
functions[validate_ai_command]=1
functions[initialize_agent_rules]=1
functions[auto_load_rules]=1
functions[check_compliance]=1
functions[generate_compliance_report]=1
functions[show_ai_rules_status]=1
functions[reload_ai_rules]=1

# Export variables
export AI_RULES_FILE AI_RULES_LOADER_VERSION AI_RULES_CACHE_DIR AI_RULES_LOG

echo "🤖 AI Rules Loader v$AI_RULES_LOADER_VERSION initialized"
echo "   Rules file: $AI_RULES_FILE"
echo "   Log file: $AI_RULES_LOG"
echo "   Auto-load: ${AI_AUTO_LOAD_RULES:-true}"
#!/bin/bash
# =============================================================================
# UNIVERSAL AI AGENT STARTUP - Automatic Rules Loading
# =============================================================================
# This script provides a universal startup mechanism for all AI agents to
# automatically load and comply with the cbwinslow AI agent rules.
# 
# Usage: Source this script at the beginning of any AI agent session:
#   source ~/.ai_agent_startup.sh
#   or
#   . ~/.ai_agent_startup.sh

# =============================================================================
# CONFIGURATION AND DETECTION
# =============================================================================

# Version and paths
AI_STARTUP_VERSION="2.0.0"
AI_RULES_FILE="${HOME}/.ai_agent_rules"
AI_RULES_LOADER="${HOME}/.ai_rules_loader.sh"
AI_INTEGRATION_PY="${HOME}/.ai_rules_integration.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# AGENT DETECTION FUNCTIONS
# =============================================================================

# Detect current AI agent environment
detect_current_agent() {
    local agent_type="unknown"
    
    # Check environment variables first
    if [[ -n "${TERM_PROGRAM:-}" ]]; then
        case "$TERM_PROGRAM" in
            "vscode"|"vscode-insiders") agent_type="vscode" ;;
            "cursor") agent_type="cursor" ;;
            "hyper") agent_type="hyper" ;;
            "wezterm") agent_type="wezterm" ;;
        esac
    fi
    
    # Check for specific AI tool indicators
    if [[ -n "${OPENAI_API_KEY:-}" && "$agent_type" == "unknown" ]]; then
        agent_type="openai_agent"
    elif [[ -n "${ANTHROPIC_API_KEY:-}" && "$agent_type" == "unknown" ]]; then
        agent_type="anthropic_agent"
    elif [[ -n "${OPENROUTER_API_KEY:-}" && "$agent_type" == "unknown" ]]; then
        agent_type="openrouter_agent"
    fi
    
    # Check for AI tool directories
    if [[ -d "$HOME/.cursor" && "$agent_type" == "unknown" ]]; then
        agent_type="cursor"
    elif [[ -d "$HOME/.continue" && "$agent_type" == "unknown" ]]; then
        agent_type="continue"
    elif [[ -d "$HOME/.cline" && "$agent_type" == "unknown" ]]; then
        agent_type="cline"
    elif [[ -d "$HOME/.codex" && "$agent_type" == "unknown" ]]; then
        agent_type="codex"
    fi
    
    # Check command line arguments or parent process
    if [[ "$agent_type" == "unknown" ]]; then
        local parent_process=$(ps -o comm= -p $PPID 2>/dev/null || echo "")
        case "$parent_process" in
            *"opencode"*) agent_type="opencode" ;;
            *"cursor"*) agent_type="cursor" ;;
            *"code"*) agent_type="vscode" ;;
            *"claude"*) agent_type="claude" ;;
            *"copilot"*) agent_type="copilot" ;;
        esac
    fi
    
    echo "$agent_type"
}

# =============================================================================
# RULES LOADING FUNCTIONS
# =============================================================================

# Load AI rules with comprehensive error handling
load_ai_rules_comprehensive() {
    local agent_name="$1"
    local session_id="${2:-$(date +%s)}"
    
    echo -e "${BLUE}🤖 Loading AI Agent Rules for: ${CYAN}$agent_name${NC}"
    
    # Check if rules file exists
    if [[ ! -f "$AI_RULES_FILE" ]]; then
        echo -e "${RED}❌ CRITICAL: AI rules file not found!${NC}"
        echo -e "${RED}   Expected at: $AI_RULES_FILE${NC}"
        echo -e "${YELLOW}⚠️  AI agents will operate without safety constraints!${NC}"
        return 1
    fi
    
    # Source the rules file
    if source "$AI_RULES_FILE"; then
        echo -e "${GREEN}✅ Core AI rules loaded successfully${NC}"
    else
        echo -e "${RED}❌ Failed to load core AI rules${NC}"
        return 1
    fi
    
    # Load rules loader if available
    if [[ -f "$AI_RULES_LOADER" ]]; then
        if source "$AI_RULES_LOADER"; then
            echo -e "${GREEN}✅ AI rules loader initialized${NC}"
        else
            echo -e "${YELLOW}⚠️  Failed to load rules loader${NC}"
        fi
    fi
    
    # Set environment variables
    export AI_RULES_ACTIVE=true
    export AI_RULES_VERSION="$AI_STARTUP_VERSION"
    export AI_AGENT_NAME="$agent_name"
    export AI_SESSION_ID="$session_id"
    export AI_RULES_LOADED_TIME="$(date '+%Y-%m-%d %H:%M:%S')"
    export AI_STARTUP_VERSION="$AI_STARTUP_VERSION"
    
    # Log the loading
    local log_entry="[$(date '+%Y-%m-%d %H:%M:%S')] AI Agent Startup v$AI_STARTUP_VERSION"
    log_entry+=" | Agent: $agent_name"
    log_entry+=" | Session: $session_id"
    log_entry+=" | Status: SUCCESS"
    
    echo "$log_entry" >> "${HOME}/logs/ai_agent_startup.log" 2>/dev/null || true
    
    echo -e "${GREEN}✅ AI Agent Rules fully loaded and active${NC}"
    return 0
}

# =============================================================================
# AGENT-SPECIFIC INITIALIZATION
# =============================================================================

# Initialize rules for specific agent types
initialize_agent_specific() {
    local agent_type="$1"
    
    case "$agent_type" in
        "vscode")
            initialize_vscode_agent
            ;;
        "cursor")
            initialize_cursor_agent
            ;;
        "opencode")
            initialize_opencode_agent
            ;;
        "claude")
            initialize_claude_agent
            ;;
        "anthropic_agent")
            initialize_anthropic_agent
            ;;
        "openai_agent")
            initialize_openai_agent
            ;;
        "openrouter_agent")
            initialize_openrouter_agent
            ;;
        *)
            initialize_generic_agent "$agent_type"
            ;;
    esac
}

# VSCode specific initialization
initialize_vscode_agent() {
    echo -e "${BLUE}🔧 Initializing VSCode agent integration${NC}"
    
    # VSCode-specific settings
    export AI_AGENT_TYPE="vscode"
    export AI_AGENT_CAPABILITIES="code_editing,file_operations,terminal_access"
    
    # Create VSCode-specific hooks if needed
    if declare -f ai_validate_operation >/dev/null 2>&1; then
        # Add VSCode-specific validation
        eval 'vscode_safe_operation() {
            local operation="$1"
            local target="$2"
            
            # Additional VSCode-specific checks
            if [[ "$target" =~ \.vscode/ ]] && [[ "$operation" =~ (rm|mv) ]]; then
                echo -e "${YELLOW}⚠️  VSCode configuration modification detected${NC}"
                echo -e "${YELLOW}   This may affect your editor settings${NC}"
            fi
            
            ai_validate_operation "$operation" "$target"
        }'
    fi
}

# Cursor specific initialization
initialize_cursor_agent() {
    echo -e "${BLUE}🔧 Initializing Cursor agent integration${NC}"
    
    export AI_AGENT_TYPE="cursor"
    export AI_AGENT_CAPABILITIES="ai_coding,code_generation,file_operations"
    
    # Cursor-specific safety measures
    if declare -f ai_validate_operation >/dev/null 2>&1; then
        eval 'cursor_safe_operation() {
            local operation="$1"
            local target="$2"
            
            # Cursor-specific validation
            if [[ "$operation" == "apply_ai_suggestion" ]]; then
                echo -e "${CYAN}🤖 Validating AI-generated code changes...${NC}"
            fi
            
            ai_validate_operation "$operation" "$target"
        }'
    fi
}

# OpenCode specific initialization
initialize_opencode_agent() {
    echo -e "${BLUE}🔧 Initializing OpenCode agent integration${NC}"
    
    export AI_AGENT_TYPE="opencode"
    export AI_AGENT_CAPABILITIES="code_analysis,automated_refactoring,documentation"
    
    # OpenCode is already designed with safety in mind
    echo -e "${GREEN}✅ OpenCode agent has built-in safety features${NC}"
}

# Claude specific initialization
initialize_claude_agent() {
    echo -e "${BLUE}🔧 Initializing Claude agent integration${NC}"
    
    export AI_AGENT_TYPE="claude"
    export AI_AGENT_CAPABILITIES="conversation,code_assistance,analysis"
    
    # Claude-specific safety
    echo -e "${CYAN}🧠 Claude agent with enhanced reasoning capabilities${NC}"
}

# Generic agent initialization
initialize_generic_agent() {
    local agent_type="$1"
    
    echo -e "${BLUE}🔧 Initializing generic agent: $agent_type${NC}"
    
    export AI_AGENT_TYPE="$agent_type"
    export AI_AGENT_CAPABILITIES="general_assistance"
}

# =============================================================================
# COMPLIANCE AND MONITORING
# =============================================================================

# Show compliance status
show_compliance_status() {
    echo -e "${PURPLE}📊 AI Agent Compliance Status${NC}"
    echo -e "${PURPLE}=============================${NC}"
    
    if [[ "$AI_RULES_ACTIVE" == "true" ]]; then
        echo -e "${GREEN}✅ Rules Status: ACTIVE${NC}"
        echo -e "${GREEN}✅ Agent Name: $AI_AGENT_NAME${NC}"
        echo -e "${GREEN}✅ Session ID: $AI_SESSION_ID${NC}"
        echo -e "${GREEN}✅ Version: $AI_RULES_VERSION${NC}"
        echo -e "${GREEN}✅ Loaded: $AI_RULES_LOADED_TIME${NC}"
        
        if [[ -n "$AI_AGENT_TYPE" ]]; then
            echo -e "${GREEN}✅ Agent Type: $AI_AGENT_TYPE${NC}"
        fi
        
        if [[ -n "$AI_AGENT_CAPABILITIES" ]]; then
            echo -e "${GREEN}✅ Capabilities: $AI_AGENT_CAPABILITIES${NC}"
        fi
    else
        echo -e "${RED}❌ Rules Status: INACTIVE${NC}"
        echo -e "${YELLOW}⚠️  Agent may operate without safety constraints${NC}"
    fi
    
    echo ""
}

# Create compliance report
create_compliance_report() {
    local report_file="${HOME}/.cache/ai_rules/compliance_report_$(date +%Y%m%d_%H%M%S).json"
    
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "agent_name": "${AI_AGENT_NAME:-unknown}",
    "agent_type": "${AI_AGENT_TYPE:-unknown}",
    "session_id": "${AI_SESSION_ID:-unknown}",
    "rules_version": "${AI_RULES_VERSION:-unknown}",
    "rules_active": "${AI_RULES_ACTIVE:-false}",
    "startup_version": "$AI_STARTUP_VERSION",
    "capabilities": "${AI_AGENT_CAPABILITIES:-unknown}",
    "loaded_time": "${AI_RULES_LOADED_TIME:-unknown}",
    "environment": {
        "shell": "$SHELL",
        "user": "$USER",
        "home": "$HOME",
        "pwd": "$PWD",
        "term_program": "${TERM_PROGRAM:-unknown}"
    }
}
EOF
    
    echo -e "${CYAN}📋 Compliance report created: $report_file${NC}"
}

# =============================================================================
# MAIN STARTUP SEQUENCE
# =============================================================================

# Main startup function
main_startup() {
    # Detect the current agent
    local current_agent=$(detect_current_agent)
    
    echo -e "${CYAN}🚀 AI Agent Startup v$AI_STARTUP_VERSION${NC}"
    echo -e "${CYAN}=====================================${NC}"
    echo -e "${BLUE}🔍 Detected Agent: ${YELLOW}$current_agent${NC}"
    echo ""
    
    # Load AI rules
    if load_ai_rules_comprehensive "$current_agent"; then
        # Initialize agent-specific features
        initialize_agent_specific "$current_agent"
        
        # Show compliance status
        show_compliance_status
        
        # Create compliance report
        create_compliance_report
        
        echo ""
        echo -e "${GREEN}🎉 AI Agent startup completed successfully!${NC}"
        echo -e "${GREEN}   All operations are now governed by AI safety rules${NC}"
        echo ""
        
        # Show quick help
        if declare -f ai_show_rules >/dev/null 2>&1; then
            echo -e "${CYAN}💡 Type 'ai_show_rules' to see detailed safety rules${NC}"
        fi
        echo -e "${CYAN}💡 Type 'show_compliance_status' to check compliance anytime${NC}"
        echo -e "${CYAN}💡 Type 'create_compliance_report' to generate detailed report${NC}"
        
    else
        echo -e "${RED}❌ AI Agent startup failed!${NC}"
        echo -e "${RED}   Agent may operate without safety constraints${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Please check that $AI_RULES_FILE exists and is readable${NC}"
        return 1
    fi
    
    return 0
}

# =============================================================================
# AUTO-EXECUTION
# =============================================================================

# Check if we should auto-run (only in interactive sessions or when explicitly requested)
if [[ "${AI_AUTO_STARTUP:-true}" == "true" ]] && [[ $- == *i* ]]; then
    main_startup
fi

# Export functions for use by agents (zsh compatible)
functions[detect_current_agent]=1
functions[load_ai_rules_comprehensive]=1
functions[initialize_agent_specific]=1
functions[show_compliance_status]=1
functions[create_compliance_report]=1

# Export variables
export AI_STARTUP_VERSION AI_RULES_FILE AI_RULES_LOADER AI_INTEGRATION_PY

echo -e "${GREEN}✅ AI Agent Startup system loaded${NC}"
#!/bin/bash
# MCP Docker Management Script
# Manages Docker-based MCP servers and gateway

set -e

COMPOSE_FILE="$HOME/.docker/compose/mcp.yml"
CONFIG_DIR="$HOME/.mcp"
DATA_DIR="$HOME/.mcp/data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if docker-compose is available
check_compose() {
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        log_error "docker-compose is not installed."
        exit 1
    fi
}

# Get docker compose command
get_compose_cmd() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

# Create necessary directories
setup_directories() {
    log_info "Setting up MCP directories..."
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    log_success "Directories created"
}

# Start MCP services
start_mcp() {
    log_info "Starting MCP services..."
    local compose_cmd=$(get_compose_cmd)

    # Set environment variables
    export GITHUB_TOKEN="${GITHUB_TOKEN:-}"

    cd "$(dirname "$COMPOSE_FILE")"
    $compose_cmd -f "$(basename "$COMPOSE_FILE")" up -d

    log_success "MCP services started"
    log_info "Gateway available at: http://localhost:3000"
    log_info "SSE endpoint at: http://localhost:3001"
}

# Stop MCP services
stop_mcp() {
    log_info "Stopping MCP services..."
    local compose_cmd=$(get_compose_cmd)

    cd "$(dirname "$COMPOSE_FILE")"
    $compose_cmd -f "$(basename "$COMPOSE_FILE")" down

    log_success "MCP services stopped"
}

# Restart MCP services
restart_mcp() {
    log_info "Restarting MCP services..."
    stop_mcp
    sleep 2
    start_mcp
}

# Show status of MCP services
status_mcp() {
    log_info "MCP Services Status:"
    local compose_cmd=$(get_compose_cmd)

    cd "$(dirname "$COMPOSE_FILE")"
    $compose_cmd -f "$(basename "$COMPOSE_FILE")" ps
}

# Show logs
logs_mcp() {
    local service="${1:-}"
    local compose_cmd=$(get_compose_cmd)

    cd "$(dirname "$COMPOSE_FILE")"
    if [ -n "$service" ]; then
        $compose_cmd -f "$(basename "$COMPOSE_FILE")" logs -f "$service"
    else
        $compose_cmd -f "$(basename "$COMPOSE_FILE")" logs -f
    fi
}

# Update MCP services
update_mcp() {
    log_info "Updating MCP services..."
    local compose_cmd=$(get_compose_cmd)

    cd "$(dirname "$COMPOSE_FILE")"
    $compose_cmd -f "$(basename "$COMPOSE_FILE")" pull
    $compose_cmd -f "$(basename "$COMPOSE_FILE")" up -d

    log_success "MCP services updated"
}

# Clean up MCP services and data
clean_mcp() {
    log_warning "This will remove all MCP containers, volumes, and data. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up MCP services..."
        local compose_cmd=$(get_compose_cmd)

        cd "$(dirname "$COMPOSE_FILE")"
        $compose_cmd -f "$(basename "$COMPOSE_FILE")" down -v --remove-orphans

        # Remove data directory
        if [ -d "$DATA_DIR" ]; then
            rm -rf "$DATA_DIR"
            log_info "Data directory removed"
        fi

        log_success "MCP services cleaned up"
    else
        log_info "Cleanup cancelled"
    fi
}

# Show help
show_help() {
    cat << EOF
MCP Docker Management Script

USAGE:
    $0 <command> [options]

COMMANDS:
    start       Start all MCP services
    stop        Stop all MCP services
    restart     Restart all MCP services
    status      Show status of MCP services
    logs        Show logs (optionally specify service name)
    update      Update MCP service images
    clean       Remove all MCP containers, volumes, and data
    setup       Initial setup of directories and configuration

SERVICES:
    mcp-gateway     Central MCP gateway and registry
    mcp-filesystem  File system operations server
    mcp-github      GitHub API integration server
    mcp-sqlite      SQLite database server
    mcp-git         Git repository operations server

EXAMPLES:
    $0 start
    $0 logs mcp-gateway
    $0 status
    $0 update

CONFIGURATION:
    Compose file: $COMPOSE_FILE
    Config dir:   $CONFIG_DIR
    Data dir:     $DATA_DIR

EOF
}

# Main script logic
main() {
    local command="$1"
    shift

    case "$command" in
        start)
            check_docker
            check_compose
            setup_directories
            start_mcp
            ;;
        stop)
            check_docker
            check_compose
            stop_mcp
            ;;
        restart)
            check_docker
            check_compose
            restart_mcp
            ;;
        status)
            check_docker
            check_compose
            status_mcp
            ;;
        logs)
            check_docker
            check_compose
            logs_mcp "$@"
            ;;
        update)
            check_docker
            check_compose
            update_mcp
            ;;
        clean)
            check_docker
            check_compose
            clean_mcp
            ;;
        setup)
            setup_directories
            log_success "MCP setup complete. Run '$0 start' to start services."
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"</content>
<parameter name="filePath">/home/foomanchu8008/.local/share/chezmoi/dot_local/bin/mcp-docker
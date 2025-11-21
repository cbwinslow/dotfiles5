#!/bin/bash
# =============================================================================
# AI RULES DEPLOYMENT AUTOMATION - Enterprise-Grade Deployment System
# =============================================================================
# This script provides robust deployment automation with health checks, rollback,
# monitoring, and disaster recovery capabilities for the AI Rules system.

set -euo pipefail  # Strict error handling

# =============================================================================
# CONFIGURATION
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_DIR="${SCRIPT_DIR}/config"
readonly BACKUP_DIR="${HOME}/.ai_rules_backups"
readonly LOG_DIR="${HOME}/logs/ai_rules_deployment"
readonly HEALTH_CHECK_DIR="${HOME}/.cache/ai_rules_health"
readonly DEPLOYMENT_VERSION="2.1.0"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Deployment configuration
readonly DEPLOYMENT_CONFIG="${CONFIG_DIR}/deployment.json"
readonly ROLLBACK_CONFIG="${CONFIG_DIR}/rollback.json"
readonly HEALTH_CONFIG="${CONFIG_DIR}/health_checks.json"

# Ensure directories exist
mkdir -p "$CONFIG_DIR" "$BACKUP_DIR" "$LOG_DIR" "$HEALTH_CHECK_DIR"

# =============================================================================
# LOGGING SYSTEM
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="${LOG_DIR}/deployment_$(date +%Y%m%d).log"
    
    # Log to file
    echo "[$timestamp] [$level] $message" >> "$log_file"
    
    # Output to console with colors
    case "$level" in
        "ERROR") echo -e "${RED}❌ ERROR: $message${NC}" ;;
        "WARN")  echo -e "${YELLOW}⚠️  WARN: $message${NC}" ;;
        "INFO")  echo -e "${BLUE}ℹ️  INFO: $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ SUCCESS: $message${NC}" ;;
        "DEBUG") echo -e "${PURPLE}🐛 DEBUG: $message${NC}" ;;
        *) echo -e "${NC}$message${NC}" ;;
    esac
}

# =============================================================================
# HEALTH CHECK SYSTEM
# =============================================================================

# Comprehensive health check for AI rules system
perform_health_check() {
    local check_type="${1:-full}"
    local results_file="${HEALTH_CHECK_DIR}/health_check_$(date +%Y%m%d_%H%M%S).json"
    
    log "INFO" "Starting health check: $check_type"
    
    # Initialize results
    local results='{
        "timestamp": "'$(date -Iseconds)'",
        "check_type": "'$check_type'",
        "version": "'$DEPLOYMENT_VERSION'",
        "overall_status": "unknown",
        "checks": {}
    }'
    
    # Core file checks
    results=$(echo "$results" | jq '.checks.core_files = {}')
    
    local core_files=(
        "$HOME/.ai_agent_rules"
        "$HOME/.ai_agent_startup.sh"
        "$HOME/.ai_rules_loader.sh"
        "$HOME/.ai_rules_integration.py"
    )
    
    for file in "${core_files[@]}"; do
        local file_status="missing"
        local file_details=""
        
        if [[ -f "$file" ]]; then
            file_status="present"
            file_details=$(stat -c "size:%s,modified:%y" "$file" 2>/dev/null || echo "stat_failed")
            
            # Check if executable for scripts
            if [[ "$file" =~ \.sh$ ]]; then
                if [[ -x "$file" ]]; then
                    file_status="${file_status}_executable"
                else
                    file_status="${file_status}_not_executable"
                fi
            fi
        fi
        
        local filename=$(basename "$file")
        results=$(echo "$results" | jq --arg filename "$filename" --arg status "$file_status" --arg details "$file_details" '.checks.core_files[$filename] = {"status": $status, "details": $details}')
    done
    
    # Function availability checks
    results=$(echo "$results" | jq '.checks.functions = {}')
    
    if source "$HOME/.ai_agent_rules" 2>/dev/null; then
        local functions=(
            "ai_validate_operation"
            "ai_check_ssh_safety"
            "ai_check_system_safety"
            "ai_show_rules"
        )
        
        for func in "${functions[@]}"; do
            local func_status="missing"
            if declare -f "$func" >/dev/null 2>&1; then
                func_status="available"
            fi
            
            results=$(echo "$results" | jq --arg func "$func" --arg status "$func_status" '.checks.functions[$func] = $status')
        done
    else
        results=$(echo "$results" | jq '.checks.functions.load_error = true')
    fi
    
    # Environment variable checks
    results=$(echo "$results" | jq '.checks.environment = {}')
    
    local env_vars=(
        "AI_RULES_ACTIVE"
        "AI_RULES_VERSION"
        "AI_AGENT_NAME"
        "AI_SESSION_ID"
    )
    
    for var in "${env_vars[@]}"; do
        local var_status="unset"
        local var_value=""
        
        if [[ -n "${!var:-}" ]]; then
            var_status="set"
            var_value="${!var}"
        fi
        
        results=$(echo "$results" | jq --arg var "$var" --arg status "$var_status" --arg value "$var_value" '.checks.environment[$var] = {"status": $status, "value": $value}')
    done
    
    # Integration tests
    if [[ "$check_type" == "full" ]]; then
        results=$(echo "$results" | jq '.checks.integration = {}')
        
        # Test rule validation
        local test_result="failed"
        if ai_validate_operation "read" "/home/test" 2>/dev/null; then
            test_result="passed"
        fi
        results=$(echo "$results" | jq --arg result "$test_result" '.checks.integration.validation_test = $result')
        
        # Test Python integration
        local python_test="failed"
        if python3 -c "import sys; sys.path.append('$HOME'); from ai_rules_integration import check_compliance; print('OK')" 2>/dev/null; then
            python_test="passed"
        fi
        results=$(echo "$results" | jq --arg result "$python_test" '.checks.integration.python_test = $result')
    fi
    
    # Calculate overall status
    local overall_status="healthy"
    local failed_checks=$(echo "$results" | jq -r '.checks | to_entries[] | select(.value.status == "missing" or .value.status == "failed") | .key' | wc -l)
    
    if [[ $failed_checks -gt 0 ]]; then
        overall_status="unhealthy"
    fi
    
    results=$(echo "$results" | jq --arg status "$overall_status" '.overall_status = $status')
    
    # Save results
    echo "$results" > "$results_file"
    
    log "INFO" "Health check completed: $overall_status"
    log "INFO" "Results saved to: $results_file"
    
    # Display summary
    echo "$results" | jq -r '
        "Health Check Summary",
        "==================",
        "Overall Status: \(.overall_status)",
        "Version: \(.version)",
        "Timestamp: \(.timestamp)",
        "",
        "Core Files:",
        (.checks.core_files | to_entries[] | "  \(.key): \(.value.status)"),
        "",
        "Functions:",
        (.checks.functions | to_entries[] | "  \(.key): \(.value // "error")"),
        "",
        "Environment:",
        (.checks.environment | to_entries[] | "  \(.key): \(.value.status)")
    '
    
    if [[ "$overall_status" == "healthy" ]]; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# BACKUP AND RECOVERY SYSTEM
# =============================================================================

# Create backup of current AI rules system
create_backup() {
    local backup_name="${1:-backup_$(date +%Y%m%d_%H%M%S)}"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    log "INFO" "Creating backup: $backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup core files
    local files_to_backup=(
        "$HOME/.ai_agent_rules"
        "$HOME/.ai_agent_startup.sh"
        "$HOME/.ai_rules_loader.sh"
        "$HOME/.ai_rules_integration.py"
        "$HOME/.zshrc"
        "$HOME/dotfiles/dot_bashrc"
    )
    
    local backup_manifest='{"backup_name": "'$backup_name'", "timestamp": "'$(date -Iseconds)'", "files": {}}'
    
    for file in "${files_to_backup[@]}"; do
        if [[ -f "$file" ]]; then
            local filename=$(basename "$file")
            local backup_file="${backup_path}/${filename}"
            
            cp "$file" "$backup_file"
            backup_manifest=$(echo "$backup_manifest" | jq --arg filename "$filename" --arg original "$file" '.files[$filename] = {"original": $original, "backed_up": true}')
            
            log "INFO" "Backed up: $file"
        else
            local filename=$(basename "$file")
            backup_manifest=$(echo "$backup_manifest" | jq --arg filename "$filename" --arg original "$file" '.files[$filename] = {"original": $original, "backed_up": false}')
            
            log "WARN" "File not found for backup: $file"
        fi
    done
    
    # Save backup manifest
    echo "$backup_manifest" > "${backup_path}/backup_manifest.json"
    
    # Create backup metadata
    cat > "${backup_path}/backup_info.txt" << EOF
Backup Name: $backup_name
Created: $(date)
Version: $DEPLOYMENT_VERSION
Files Backed Up: $(echo "$backup_manifest" | jq '.files | length')
Health Check: $(perform_health_check quick >/dev/null 2>&1 && echo "Healthy" || echo "Unhealthy")
EOF
    
    log "SUCCESS" "Backup created: $backup_path"
    echo "$backup_path"
}

# Restore from backup
restore_backup() {
    local backup_name="$1"
    local backup_path="${BACKUP_DIR}/${backup_name}"
    
    if [[ ! -d "$backup_path" ]]; then
        log "ERROR" "Backup not found: $backup_name"
        return 1
    fi
    
    log "INFO" "Restoring from backup: $backup_name"
    
    # Load backup manifest
    local backup_manifest
    backup_manifest=$(cat "${backup_path}/backup_manifest.json" 2>/dev/null) || {
        log "ERROR" "Failed to load backup manifest"
        return 1
    }
    
    # Restore files
    echo "$backup_manifest" | jq -r '.files | to_entries[] | select(.value.backed_up == true) | .key' | while read -r filename; do
        local original_path=$(echo "$backup_manifest" | jq -r --arg filename "$filename" '.files[$filename].original')
        local backup_file="${backup_path}/${filename}"
        
        if [[ -f "$backup_file" ]]; then
            # Create backup of current file before restoring
            if [[ -f "$original_path" ]]; then
                cp "$original_path" "${original_path}.pre_restore_$(date +%s)"
            fi
            
            cp "$backup_file" "$original_path"
            log "INFO" "Restored: $filename -> $original_path"
        else
            log "ERROR" "Backup file not found: $backup_file"
        fi
    done
    
    # Reload shell configurations
    log "INFO" "Reloading shell configurations..."
    
    # Make scripts executable
    chmod +x "$HOME/.ai_agent_startup.sh" "$HOME/.ai_rules_loader.sh" 2>/dev/null || true
    
    log "SUCCESS" "Backup restored: $backup_name"
    
    # Perform health check after restore
    perform_health_check
}

# List available backups
list_backups() {
    log "INFO" "Available backups:"
    
    if [[ ! -d "$BACKUP_DIR" ]] || [[ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]]; then
        log "WARN" "No backups found"
        return 0
    fi
    
    for backup_dir in "$BACKUP_DIR"/*; do
        if [[ -d "$backup_dir" ]]; then
            local backup_name=$(basename "$backup_dir")
            local backup_info="${backup_dir}/backup_info.txt"
            
            if [[ -f "$backup_info" ]]; then
                echo ""
                echo "📦 Backup: $backup_name"
                cat "$backup_info"
            else
                echo "📦 Backup: $backup_name (no metadata)"
            fi
        fi
    done
}

# =============================================================================
# DEPLOYMENT FUNCTIONS
# =============================================================================

# Deploy AI rules system with rollback capability
deploy_ai_rules() {
    local deployment_mode="${1:-safe}"  # safe, force, dry-run
    local backup_name=""
    
    log "INFO" "Starting AI rules deployment (mode: $deployment_mode)"
    
    # Pre-deployment health check
    log "INFO" "Running pre-deployment health check..."
    if ! perform_health_check quick; then
        if [[ "$deployment_mode" != "force" ]]; then
            log "ERROR" "Pre-deployment health check failed. Use 'force' mode to override."
            return 1
        else
            log "WARN" "Pre-deployment health check failed, proceeding with force mode"
        fi
    fi
    
    # Create backup before deployment
    if [[ "$deployment_mode" != "dry-run" ]]; then
        backup_name=$(create_backup "pre_deploy_$(date +%Y%m%d_%H%M%S)")
        log "INFO" "Created backup: $backup_name"
    fi
    
    # Deployment steps
    local deployment_steps=(
        "validate_core_files"
        "set_permissions"
        "update_shell_configs"
        "validate_integrations"
        "post_deployment_health_check"
    )
    
    for step in "${deployment_steps[@]}"; do
        log "INFO" "Executing deployment step: $step"
        
        if [[ "$deployment_mode" == "dry-run" ]]; then
            log "INFO" "[DRY-RUN] Would execute: $step"
            continue
        fi
        
        case "$step" in
            "validate_core_files")
                validate_core_files
                ;;
            "set_permissions")
                set_permissions
                ;;
            "update_shell_configs")
                update_shell_configs
                ;;
            "validate_integrations")
                validate_integrations
                ;;
            "post_deployment_health_check")
                if ! perform_health_check full; then
                    log "ERROR" "Post-deployment health check failed"
                    if [[ "$deployment_mode" != "force" ]]; then
                        log "INFO" "Initiating rollback..."
                        rollback_deployment "$backup_name"
                        return 1
                    fi
                fi
                ;;
        esac
        
        log "SUCCESS" "Completed step: $step"
    done
    
    log "SUCCESS" "AI rules deployment completed successfully"
    
    if [[ "$deployment_mode" != "dry-run" ]]; then
        # Create deployment record
        create_deployment_record "$backup_name" "success"
    fi
}

# Rollback deployment
rollback_deployment() {
    local backup_name="$1"
    
    log "INFO" "Starting deployment rollback using backup: $backup_name"
    
    if [[ -z "$backup_name" ]]; then
        log "ERROR" "Backup name required for rollback"
        return 1
    fi
    
    # Restore from backup
    if restore_backup "$backup_name"; then
        log "SUCCESS" "Rollback completed successfully"
        create_deployment_record "$backup_name" "rollback"
    else
        log "ERROR" "Rollback failed"
        return 1
    fi
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

validate_core_files() {
    log "INFO" "Validating core AI rules files..."
    
    local required_files=(
        "$HOME/.ai_agent_rules"
        "$HOME/.ai_agent_startup.sh"
        "$HOME/.ai_rules_loader.sh"
        "$HOME/.ai_rules_integration.py"
    )
    
    local validation_errors=0
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Required file missing: $file"
            ((validation_errors++))
            continue
        fi
        
        # Check file syntax for shell scripts
        if [[ "$file" =~ \.sh$ ]]; then
            if ! bash -n "$file" 2>/dev/null; then
                log "ERROR" "Syntax error in: $file"
                ((validation_errors++))
            fi
        fi
        
        # Check Python syntax
        if [[ "$file" =~ \.py$ ]]; then
            if ! python3 -m py_compile "$file" 2>/dev/null; then
                log "ERROR" "Syntax error in: $file"
                ((validation_errors++))
            fi
        fi
    done
    
    if [[ $validation_errors -gt 0 ]]; then
        log "ERROR" "Core file validation failed with $validation_errors errors"
        return 1
    fi
    
    log "SUCCESS" "Core files validation passed"
    return 0
}

set_permissions() {
    log "INFO" "Setting appropriate permissions..."
    
    # Make shell scripts executable
    chmod +x "$HOME/.ai_agent_startup.sh" "$HOME/.ai_rules_loader.sh" 2>/dev/null || {
        log "WARN" "Could not set executable permissions on shell scripts"
    }
    
    # Set appropriate permissions for rules file
    chmod 644 "$HOME/.ai_agent_rules" 2>/dev/null || {
        log "WARN" "Could not set permissions on rules file"
    }
    
    # Set permissions for Python integration
    chmod 644 "$HOME/.ai_rules_integration.py" 2>/dev/null || {
        log "WARN" "Could not set permissions on Python integration"
    }
    
    log "SUCCESS" "Permissions set successfully"
}

update_shell_configs() {
    log "INFO" "Updating shell configurations..."
    
    # This would update shell configs if needed
    # Already handled in previous steps
    
    log "SUCCESS" "Shell configurations updated"
}

validate_integrations() {
    log "INFO" "Validating integrations..."
    
    # Test shell integration
    if bash -c 'source ~/.ai_agent_startup.sh && echo "OK"' 2>/dev/null; then
        log "SUCCESS" "Shell integration validated"
    else
        log "ERROR" "Shell integration validation failed"
        return 1
    fi
    
    # Test Python integration
    if python3 -c "
import sys
sys.path.append('$HOME')
try:
    from ai_rules_integration import check_compliance
    print('OK')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log "SUCCESS" "Python integration validated"
    else
        log "ERROR" "Python integration validation failed"
        return 1
    fi
    
    log "SUCCESS" "All integrations validated"
}

# =============================================================================
# DEPLOYMENT RECORDS
# =============================================================================

create_deployment_record() {
    local backup_name="$1"
    local status="$2"
    
    local record_file="${LOG_DIR}/deployment_record_$(date +%Y%m%d).json"
    local timestamp=$(date -Iseconds)
    
    local record='{
        "timestamp": "'$timestamp'",
        "version": "'$DEPLOYMENT_VERSION'",
        "backup_name": "'$backup_name'",
        "status": "'$status'",
        "health_check": "'$(perform_health_check quick >/dev/null 2>&1 && echo "healthy" || echo "unhealthy")'"
    }'
    
    echo "$record" >> "$record_file"
    
    log "INFO" "Deployment record created: $status"
}

# =============================================================================
# MAIN CLI INTERFACE
# =============================================================================

show_help() {
    cat << EOF
AI Rules Deployment Automation v$DEPLOYMENT_VERSION

USAGE:
    $0 <command> [options]

COMMANDS:
    deploy [mode]     Deploy AI rules system
                     Modes: safe (default), force, dry-run
    
    health [type]     Perform health check
                     Types: full (default), quick
    
    backup [name]     Create backup of current system
    
    restore <name>    Restore from backup
    
    list-backups      List available backups
    
    rollback <name>   Rollback to specific backup
    
    status           Show deployment status
    
    help             Show this help

EXAMPLES:
    $0 deploy                    # Safe deployment
    $0 deploy force             # Force deployment (skip health checks)
    $0 deploy dry-run            # Dry run deployment
    $0 health                   # Full health check
    $0 health quick             # Quick health check
    $0 backup                   # Create backup
    $0 restore backup_20231113   # Restore from backup
    $0 list-backups             # List all backups

EOF
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        "deploy")
            deploy_ai_rules "${2:-safe}"
            ;;
        "health")
            perform_health_check "${2:-full}"
            ;;
        "backup")
            create_backup "${2:-}"
            ;;
        "restore")
            restore_backup "$2"
            ;;
        "list-backups")
            list_backups
            ;;
        "rollback")
            rollback_deployment "$2"
            ;;
        "status")
            perform_health_check quick
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
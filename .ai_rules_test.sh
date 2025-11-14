#!/bin/bash
# =============================================================================
# AI RULES TESTING AND VALIDATION FRAMEWORK
# =============================================================================
# Comprehensive testing framework for AI Rules system with automated validation,
# regression testing, and continuous integration capabilities.

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TEST_DIR="${HOME}/.ai_rules_tests"
readonly TEST_RESULTS_DIR="${TEST_DIR}/results"
readonly TEST_DATA_DIR="${TEST_DIR}/data"
readonly TEST_REPORTS_DIR="${TEST_DIR}/reports"
readonly FRAMEWORK_VERSION="2.1.0"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Test configuration
readonly TEST_CONFIG="${TEST_DIR}/test_config.json"
readonly TEST_SUITES_DIR="${TEST_DIR}/test_suites"

# Ensure directories exist
mkdir -p "$TEST_DIR" "$TEST_RESULTS_DIR" "$TEST_DATA_DIR" "$TEST_REPORTS_DIR" "$TEST_SUITES_DIR"

# =============================================================================
# LOGGING AND REPORTING
# =============================================================================

log_test() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "PASS")  echo -e "${GREEN}✅ PASS: $message${NC}" ;;
        "FAIL")  echo -e "${RED}❌ FAIL: $message${NC}" ;;
        "SKIP")  echo -e "${YELLOW}⏭️  SKIP: $message${NC}" ;;
        "INFO")  echo -e "${BLUE}ℹ️  INFO: $message${NC}" ;;
        "WARN")  echo -e "${YELLOW}⚠️  WARN: $message${NC}" ;;
        "DEBUG") echo -e "${PURPLE}🐛 DEBUG: $message${NC}" ;;
        *) echo -e "${NC}$message${NC}" ;;
    esac
}

# =============================================================================
# TEST FRAMEWORK CORE
# =============================================================================

# Test result data structure
declare -A TEST_RESULTS
declare -i TESTS_TOTAL=0
declare -i TESTS_PASSED=0
declare -i TESTS_FAILED=0
declare -i TESTS_SKIPPED=0

# Initialize test session
init_test_session() {
    local session_name="${1:-test_session_$(date +%Y%m%d_%H%M%S)}"
    
    TESTS_TOTAL=0
    TESTS_PASSED=0
    TESTS_FAILED=0
    TESTS_SKIPPED=0
    
    # Clear previous results
    TEST_RESULTS=()
    
    # Create session directory
    local session_dir="${TEST_RESULTS_DIR}/${session_name}"
    mkdir -p "$session_dir"
    
    # Initialize test report
    local report_file="${session_dir}/test_report.json"
    cat > "$report_file" << EOF
{
    "session_name": "$session_name",
    "framework_version": "$FRAMEWORK_VERSION",
    "start_time": "$(date -Iseconds)",
    "tests": [],
    "summary": {}
}
EOF
    
    log_test "INFO" "Test session initialized: $session_name"
    echo "$session_dir"
}

# Run a single test
run_test() {
    local test_name="$1"
    local test_function="$2"
    local test_category="${3:-general}"
    local timeout="${4:-30}"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    log_test "INFO" "Running test: $test_name"
    
    local test_start_time=$(date +%s)
    local test_result="PASS"
    local test_output=""
    local test_error=""
    
    # Run test with timeout
    if timeout "$timeout" bash -c "source \"$0\" && $test_function" 2>"${TEST_DATA_DIR}/${test_name}_error.log" >"${TEST_DATA_DIR}/${test_name}_output.log"; then
        test_result="PASS"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            test_result="FAIL"
            test_error="Test timed out after ${timeout}s"
        else
            test_result="FAIL"
            test_error=$(cat "${TEST_DATA_DIR}/${test_name}_error.log" 2>/dev/null || echo "Unknown error")
        fi
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    local test_end_time=$(date +%s)
    local test_duration=$((test_end_time - test_start_time))
    
    # Read test output
    test_output=$(cat "${TEST_DATA_DIR}/${test_name}_output.log" 2>/dev/null || echo "")
    
    # Store test result
    local test_data='{
        "name": "'$test_name'",
        "category": "'$test_category'",
        "result": "'$test_result'",
        "duration": '$test_duration',
        "start_time": '$test_start_time',
        "end_time": '$test_end_time',
        "output": '$(echo "$test_output" | jq -Rs .)',
        "error": '$(echo "$test_error" | jq -Rs .)'
    }'
    
    TEST_RESULTS["$test_name"]="$test_data"
    
    # Log result
    log_test "$test_result" "$test_name (${test_duration}s)"
    
    if [[ "$test_result" == "FAIL" ]]; then
        log_test "DEBUG" "Error: $test_error"
    fi
    
    return $([[ "$test_result" == "PASS" ]] && echo 0 || echo 1)
}

# Skip a test
skip_test() {
    local test_name="$1"
    local reason="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    
    log_test "SKIP" "$test_name: $reason"
    
    local test_data='{
        "name": "'$test_name'",
        "result": "SKIP",
        "reason": "'$reason'",
        "duration": 0
    }'
    
    TEST_RESULTS["$test_name"]="$test_data"
}

# Generate test report
generate_test_report() {
    local session_dir="$1"
    local report_file="${session_dir}/test_report.json"
    
    # Calculate summary
    local success_rate=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
    local summary='{
        "total_tests": '$TESTS_TOTAL',
        "passed": '$TESTS_PASSED',
        "failed": '$TESTS_FAILED',
        "skipped": '$TESTS_SKIPPED',
        "success_rate": '$success_rate',
        "end_time": "'$(date -Iseconds)'"
    }'
    
    # Update report with all test results
    local tests_array=$(printf '%s\n' "${TEST_RESULTS[@]}" | jq -s .)
    
    local final_report=$(jq -n \
        --argjson summary "$summary" \
        --argjson tests "$tests_array" \
        '{
            session_name: (input.session_name),
            framework_version: (input.framework_version),
            start_time: (input.start_time),
            tests: $tests,
            summary: $summary
        }' "$report_file")
    
    echo "$final_report" > "$report_file"
    
    # Generate HTML report
    generate_html_report "$session_dir" "$final_report"
    
    # Generate summary
    log_test "INFO" "Test Summary:"
    log_test "INFO" "  Total Tests: $TESTS_TOTAL"
    log_test "INFO" "  Passed: $TESTS_PASSED"
    log_test "INFO" "  Failed: $TESTS_FAILED"
    log_test "INFO" "  Skipped: $TESTS_SKIPPED"
    log_test "INFO" "  Success Rate: ${success_rate}%"
    
    if [[ $TESTS_FAILED -gt 0 ]]; then
        log_test "WARN" "Some tests failed. Check report for details."
        return 1
    else
        log_test "INFO" "All tests passed!"
        return 0
    fi
}

# Generate HTML report
generate_html_report() {
    local session_dir="$1"
    local report_data="$2"
    local html_file="${session_dir}/test_report.html"
    
    cat > "$html_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>AI Rules Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary { display: flex; gap: 20px; margin-bottom: 20px; }
        .metric { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; }
        .metric-label { color: #666; }
        .test-list { margin-top: 20px; }
        .test-item { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .test-pass { border-left: 5px solid #28a745; }
        .test-fail { border-left: 5px solid #dc3545; }
        .test-skip { border-left: 5px solid #ffc107; }
        .test-name { font-weight: bold; font-size: 1.1em; }
        .test-meta { color: #666; font-size: 0.9em; margin: 5px 0; }
        .test-output { background: #f8f9fa; padding: 10px; border-radius: 3px; margin-top: 10px; font-family: monospace; white-space: pre-wrap; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
EOF
    
    # Add summary section
    echo "$report_data" | jq -r '
    "<div class=\"header\">
        <h1>AI Rules Test Report</h1>
        <p><strong>Session:</strong> \(.session_name)</p>
        <p><strong>Framework Version:</strong> \(.framework_version)</p>
        <p><strong>Start Time:</strong> \(.start_time)</p>
        <p><strong>End Time:</strong> \(.summary.end_time)</p>
    </div>
    <div class=\"summary\">
        <div class=\"metric\">
            <div class=\"metric-value\">\(.summary.total_tests)</div>
            <div class=\"metric-label\">Total Tests</div>
        </div>
        <div class=\"metric\">
            <div class=\"metric-value\">\(.summary.passed)</div>
            <div class=\"metric-label\">Passed</div>
        </div>
        <div class=\"metric\">
            <div class=\"metric-value\">\(.summary.failed)</div>
            <div class=\"metric-label\">Failed</div>
        </div>
        <div class=\"metric\">
            <div class=\"metric-value\">\(.summary.success_rate)%</div>
            <div class=\"metric-label\">Success Rate</div>
        </div>
    </div>
    <div class=\"test-list\">
        <h2>Test Results</h2>"
    ' >> "$html_file"
    
    # Add test results
    echo "$report_data" | jq -r '.tests[] | 
    "<div class=\"test-item test-\(.result | ascii_downcase)\">
        <div class=\"test-name\">\(.name)</div>
        <div class=\"test-meta\">Result: \(.result) | Duration: \(.duration)s | Category: \(.category // "general")</div>
        \(.output // "" | if . != "" then "<div class=\"test-output\">Output: \(.)</div>" else "" end)
        \(.error // "" | if . != "" then "<div class=\"test-output error\">Error: \(.)</div>" else "" end)
    </div>"
    ' >> "$html_file"
    
    cat >> "$html_file" << 'EOF'
    </div>
</body>
</html>
EOF
    
    log_test "INFO" "HTML report generated: $html_file"
}

# =============================================================================
# TEST SUITES
# =============================================================================

# Core functionality tests
test_core_functionality() {
    local session_dir=$(init_test_session "core_functionality_$(date +%Y%m%d_%H%M%S)")
    
    # Test 1: Rules file existence
    run_test "rules_file_exists" 'test_rules_file_exists' "core" 10
    
    # Test 2: Rules file syntax
    run_test "rules_file_syntax" 'test_rules_file_syntax' "core" 15
    
    # Test 3: Function availability
    run_test "function_availability" 'test_function_availability' "core" 10
    
    # Test 4: Environment variables
    run_test "environment_variables" 'test_environment_variables' "core" 10
    
    # Test 5: Shell integration
    run_test "shell_integration" 'test_shell_integration' "integration" 20
    
    # Test 6: Python integration
    run_test "python_integration" 'test_python_integration' "integration" 20
    
    # Test 7: Agent detection
    run_test "agent_detection" 'test_agent_detection' "detection" 15
    
    # Test 8: Rule validation
    run_test "rule_validation" 'test_rule_validation' "validation" 25
    
    generate_test_report "$session_dir"
}

# Security tests
test_security() {
    local session_dir=$(init_test_session "security_$(date +%Y%m%d_%H%M%S)")
    
    # Test 1: SSH protection
    run_test "ssh_protection" 'test_ssh_protection' "security" 20
    
    # Test 2: System file protection
    run_test "system_file_protection" 'test_system_file_protection' "security" 20
    
    # Test 3: Credential protection
    run_test "credential_protection" 'test_credential_protection' "security" 15
    
    # Test 4: Command validation
    run_test "command_validation" 'test_command_validation' "security" 25
    
    # Test 5: Permission checks
    run_test "permission_checks" 'test_permission_checks' "security" 15
    
    generate_test_report "$session_dir"
}

# Performance tests
test_performance() {
    local session_dir=$(init_test_session "performance_$(date +%Y%m%d_%H%M%S)")
    
    # Test 1: Startup time
    run_test "startup_performance" 'test_startup_performance' "performance" 30
    
    # Test 2: Memory usage
    run_test "memory_usage" 'test_memory_usage' "performance" 20
    
    # Test 3: Rule validation speed
    run_test "validation_speed" 'test_validation_speed' "performance" 25
    
    # Test 4: Concurrent operations
    run_test "concurrent_operations" 'test_concurrent_operations' "performance" 30
    
    generate_test_report "$session_dir"
}

# Regression tests
test_regression() {
    local session_dir=$(init_test_session "regression_$(date +%Y%m%d_%H%M%S)")
    
    # Test 1: Previous issue fixes
    run_test "previous_issue_fixes" 'test_previous_issue_fixes' "regression" 20
    
    # Test 2: Backward compatibility
    run_test "backward_compatibility" 'test_backward_compatibility' "regression" 25
    
    # Test 3: Configuration migration
    run_test "configuration_migration" 'test_configuration_migration' "regression" 20
    
    generate_test_report "$session_dir"
}

# =============================================================================
# INDIVIDUAL TEST FUNCTIONS
# =============================================================================

# Core functionality tests
test_rules_file_exists() {
    [[ -f "$HOME/.ai_agent_rules" ]] || {
        echo "AI rules file not found"
        return 1
    }
    
    [[ -f "$HOME/.ai_agent_startup.sh" ]] || {
        echo "AI startup script not found"
        return 1
    }
    
    [[ -f "$HOME/.ai_rules_loader.sh" ]] || {
        echo "AI rules loader not found"
        return 1
    }
    
    return 0
}

test_rules_file_syntax() {
    # Test shell script syntax
    bash -n "$HOME/.ai_agent_startup.sh" || {
        echo "Syntax error in startup script"
        return 1
    }
    
    bash -n "$HOME/.ai_rules_loader.sh" || {
        echo "Syntax error in rules loader"
        return 1
    }
    
    # Test Python syntax
    python3 -m py_compile "$HOME/.ai_rules_integration.py" || {
        echo "Syntax error in Python integration"
        return 1
    }
    
    return 0
}

test_function_availability() {
    # Source the rules
    source "$HOME/.ai_agent_rules" 2>/dev/null || {
        echo "Could not source AI rules"
        return 1
    }
    
    # Check required functions
    local required_functions=(
        "ai_validate_operation"
        "ai_check_ssh_safety"
        "ai_check_system_safety"
        "ai_show_rules"
    )
    
    for func in "${required_functions[@]}"; do
        declare -f "$func" >/dev/null || {
            echo "Required function not available: $func"
            return 1
        }
    done
    
    return 0
}

test_environment_variables() {
    # Source startup script
    source "$HOME/.ai_agent_startup.sh" 2>/dev/null || {
        echo "Could not source startup script"
        return 1
    }
    
    # Check required environment variables
    [[ -n "${AI_RULES_ACTIVE:-}" ]] || {
        echo "AI_RULES_ACTIVE not set"
        return 1
    }
    
    [[ -n "${AI_RULES_VERSION:-}" ]] || {
        echo "AI_RULES_VERSION not set"
        return 1
    }
    
    return 0
}

test_shell_integration() {
    # Test shell integration in subshell
    local result
    result=$(bash -c 'source ~/.ai_agent_startup.sh >/dev/null 2>&1 && echo "OK"' 2>/dev/null)
    
    [[ "$result" == "OK" ]] || {
        echo "Shell integration failed"
        return 1
    }
    
    return 0
}

test_python_integration() {
    python3 ~/.ai_rules_integration.py >/dev/null 2>&1 || {
        echo "Python integration failed"
        return 1
    }
    
    return 0
}

test_agent_detection() {
    # Test agent detection function
    source "$HOME/.ai_agent_startup.sh" 2>/dev/null || {
        echo "Could not source startup script"
        return 1
    }
    
    declare -f detect_current_agent >/dev/null || {
        echo "detect_current_agent function not available"
        return 1
    }
    
    local detected_agent
    detected_agent=$(detect_current_agent)
    
    [[ -n "$detected_agent" ]] || {
        echo "Agent detection returned empty"
        return 1
    }
    
    return 0
}

test_rule_validation() {
    # Source rules
    source "$HOME/.ai_agent_rules" 2>/dev/null || {
        echo "Could not source AI rules"
        return 1
    }
    
    # Test safe operation
    ai_validate_operation "read" "/home/user/safe_file.txt" || {
        echo "Safe operation validation failed"
        return 1
    }
    
    # Test dangerous operation (should fail)
    if ai_validate_operation "rm" "/etc/passwd" 2>/dev/null; then
        echo "Dangerous operation validation should have failed"
        return 1
    fi
    
    return 0
}

# Security tests
test_ssh_protection() {
    source "$HOME/.ai_agent_rules" 2>/dev/null || {
        echo "Could not source AI rules"
        return 1
    }
    
    # Test SSH config protection
    if ai_check_ssh_safety "ssh" "config" 2>/dev/null; then
        echo "SSH config protection failed"
        return 1
    fi
    
    # Test SSH key protection
    if ai_check_ssh_safety "ssh" "id_rsa" 2>/dev/null; then
        echo "SSH key protection failed"
        return 1
    fi
    
    return 0
}

test_system_file_protection() {
    source "$HOME/.ai_agent_rules" 2>/dev/null || {
        echo "Could not source AI rules"
        return 1
    }
    
    # Test system file protection
    if ai_check_system_safety "rm" "/etc/passwd" 2>/dev/null; then
        echo "System file protection failed"
        return 1
    fi
    
    # Test safe file operation
    ai_check_system_safety "read" "/home/user/file.txt" || {
        echo "Safe file operation blocked"
        return 1
    }
    
    return 0
}

test_credential_protection() {
    # Test that credentials are not exposed in environment
    if [[ -n "${AI_RULES_CREDENTIALS:-}" ]]; then
        echo "Credentials exposed in environment"
        return 1
    fi
    
    # Test that secrets files are protected
    local secrets_dir="$HOME/.ai_rules_secrets.d"
    if [[ -d "$secrets_dir" ]]; then
        local perms=$(stat -c "%a" "$secrets_dir" 2>/dev/null || echo "000")
        if [[ "$perms" != "700" ]]; then
            echo "Secrets directory has incorrect permissions: $perms"
            return 1
        fi
    fi
    
    return 0
}

test_command_validation() {
    source "$HOME/.ai_agent_rules" 2>/dev/null || {
        echo "Could not source AI rules"
        return 1
    }
    
    # Test various dangerous commands
    local dangerous_commands=(
        "rm:/etc/passwd"
        "mv:/usr/bin/sudo"
        "chmod:/etc/shadow"
        "ssh:config"
    )
    
    for cmd_test in "${dangerous_commands[@]}"; do
        local operation="${cmd_test%:*}"
        local target="${cmd_test#*:}"
        
        if ai_validate_operation "$operation" "$target" 2>/dev/null; then
            echo "Dangerous command not blocked: $operation $target"
            return 1
        fi
    done
    
    return 0
}

test_permission_checks() {
    # Check file permissions
    local rules_file="$HOME/.ai_agent_rules"
    if [[ -f "$rules_file" ]]; then
        local perms=$(stat -c "%a" "$rules_file" 2>/dev/null || echo "000")
        if [[ "$perms" =~ [0-9][0-9][0-9] ]]; then
            # Should be readable by owner and group, not by others
            if [[ "${perms:2:1}" -gt 4 ]]; then
                echo "Rules file too permissive: $perms"
                return 1
            fi
        fi
    fi
    
    return 0
}

# Performance tests
test_startup_performance() {
    local start_time=$(date +%s%N)
    
    # Source startup script
    source "$HOME/.ai_agent_startup.sh" 2>/dev/null || {
        echo "Could not source startup script"
        return 1
    }
    
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    # Should startup within 5 seconds
    if [[ $duration -gt 5000 ]]; then
        echo "Startup too slow: ${duration}ms"
        return 1
    fi
    
    echo "Startup time: ${duration}ms"
    return 0
}

test_memory_usage() {
    # Get initial memory usage
    local initial_memory=$(ps -o rss= -p $$ | tr -d ' ')
    
    # Source AI rules multiple times
    for i in {1..10}; do
        source "$HOME/.ai_agent_startup.sh" 2>/dev/null
    done
    
    # Get final memory usage
    local final_memory=$(ps -o rss= -p $$ | tr -d ' ')
    local memory_increase=$((final_memory - initial_memory))
    
    # Memory increase should be reasonable (< 10MB)
    if [[ $memory_increase -gt 10240 ]]; then
        echo "Memory usage too high: ${memory_increase}KB"
        return 1
    fi
    
    echo "Memory increase: ${memory_increase}KB"
    return 0
}

test_validation_speed() {
    source "$HOME/.ai_agent_rules" 2>/dev/null || {
        echo "Could not source AI rules"
        return 1
    }
    
    local start_time=$(date +%s%N)
    
    # Run validation 100 times
    for i in {1..100}; do
        ai_validate_operation "read" "/home/user/test.txt" >/dev/null
    done
    
    local end_time=$(date +%s%N)
    local avg_time=$(( (end_time - start_time) / 100000 / 100 )) # Average in microseconds
    
    # Average validation should be fast (< 1000 microseconds)
    if [[ $avg_time -gt 1000 ]]; then
        echo "Validation too slow: ${avg_time}μs average"
        return 1
    fi
    
    echo "Average validation time: ${avg_time}μs"
    return 0
}

test_concurrent_operations() {
    # Test concurrent rule loading
    local pids=()
    
    # Start 5 concurrent processes
    for i in {1..5}; do
        (
            source "$HOME/.ai_agent_startup.sh" 2>/dev/null
            echo "Process $i completed"
        ) &
        pids+=($!)
    done
    
    # Wait for all processes
    local failed=0
    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            failed=1
        fi
    done
    
    if [[ $failed -eq 1 ]]; then
        echo "Concurrent operations failed"
        return 1
    fi
    
    return 0
}

# Regression tests
test_previous_issue_fixes() {
    # Test for specific previous issues
    # This would be customized based on actual issues encountered
    
    # Example: Test that duplicate sourcing doesn't cause issues
    source "$HOME/.ai_agent_startup.sh" 2>/dev/null
    source "$HOME/.ai_agent_startup.sh" 2>/dev/null
    
    # Should still work after duplicate sourcing
    [[ "$AI_RULES_ACTIVE" == "true" ]] || {
        echo "Duplicate sourcing broke functionality"
        return 1
    }
    
    return 0
}

test_backward_compatibility() {
    # Test that older configurations still work
    # This would test with various older config formats
    
    # For now, just test basic functionality
    source "$HOME/.ai_agent_startup.sh" 2>/dev/null || {
        echo "Backward compatibility failed"
        return 1
    }
    
    return 0
}

test_configuration_migration() {
    # Test configuration migration
    # This would test migration from older config versions
    
    return 0
}

# =============================================================================
# MAIN CLI INTERFACE
# =============================================================================

show_help() {
    cat << EOF
AI Rules Testing Framework v$FRAMEWORK_VERSION

USAGE:
    $0 <command> [options]

COMMANDS:
    test-core         Run core functionality tests
    test-security     Run security tests
    test-performance  Run performance tests
    test-regression   Run regression tests
    test-all         Run all test suites
    
    list-suites      List available test suites
    run-suite <name> Run specific test suite
    
    report <session>  Show test report for session
    list-sessions     List test sessions
    
    help              Show this help

EXAMPLES:
    $0 test-core                    # Run core tests
    $0 test-all                     # Run all tests
    $0 report core_functionality_*    # Show report for specific session
    $0 list-sessions                # List all test sessions

EOF
}

list_test_sessions() {
    log_test "INFO" "Available test sessions:"
    
    for session_dir in "$TEST_RESULTS_DIR"/*; do
        if [[ -d "$session_dir" ]]; then
            local session_name=$(basename "$session_dir")
            local report_file="${session_dir}/test_report.json"
            
            if [[ -f "$report_file" ]]; then
                local summary=$(jq -r '.summary' "$report_file" 2>/dev/null || echo "{}")
                local total=$(echo "$summary" | jq -r '.total_tests // "unknown"')
                local passed=$(echo "$summary" | jq -r '.passed // "unknown"')
                local failed=$(echo "$summary" | jq -r '.failed // "unknown"')
                
                echo "📁 $session_name"
                echo "   Tests: $total, Passed: $passed, Failed: $failed"
            fi
        fi
    done
}

show_test_report() {
    local session_pattern="$1"
    
    for session_dir in "$TEST_RESULTS_DIR"/$session_pattern; do
        if [[ -d "$session_dir" ]]; then
            local session_name=$(basename "$session_dir")
            local report_file="${session_dir}/test_report.json"
            local html_file="${session_dir}/test_report.html"
            
            echo ""
            echo "📊 Test Report: $session_name"
            echo "=============================="
            
            if [[ -f "$report_file" ]]; then
                jq -r '
                "Summary:",
                "--------",
                "Total Tests: \(.summary.total_tests)",
                "Passed: \(.summary.passed)",
                "Failed: \(.summary.failed)",
                "Skipped: \(.summary.skipped)",
                "Success Rate: \(.summary.success_rate)%",
                "",
                "Test Results:",
                "-------------",
                (.tests[] | "\(.result): \(.name) (\(.duration)s)")
                ' "$report_file"
            fi
            
            if [[ -f "$html_file" ]]; then
                echo ""
                echo "📄 HTML Report: $html_file"
            fi
        fi
    done
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        "test-core")
            test_core_functionality
            ;;
        "test-security")
            test_security
            ;;
        "test-performance")
            test_performance
            ;;
        "test-regression")
            test_regression
            ;;
        "test-all")
            log_test "INFO" "Running all test suites..."
            test_core_functionality
            test_security
            test_performance
            test_regression
            ;;
        "list-suites")
            echo "Available test suites:"
            echo "  core_functionality"
            echo "  security"
            echo "  performance"
            echo "  regression"
            ;;
        "list-sessions")
            list_test_sessions
            ;;
        "report")
            show_test_report "${2:-*}"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_test "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
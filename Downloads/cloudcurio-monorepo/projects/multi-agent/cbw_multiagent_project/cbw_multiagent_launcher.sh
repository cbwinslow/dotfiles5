#!/usr/bin/env bash
# Script Name : cbw_multiagent_launcher.sh
# Author      : cbwinslow + ChatGPT
# Date        : 2025-11-16
#
# Summary:
#   Convenience launcher for the CBW Multi-Agent CrewAI bridge.
#   - Verifies Python and dependencies.
#   - Runs the CrewAI bridge script with a provided topic.
#
# Usage:
#   ./cbw_multiagent_launcher.sh "your topic here"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREWAI_DIR="${SCRIPT_DIR}/crewai"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 "topic string for the crew""
  exit 1
fi

TOPIC="$1"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found in PATH."
  exit 1
fi

if [[ -f "${SCRIPT_DIR}/requirements.txt" ]]; then
  echo ">>> Installing/ensuring Python dependencies from requirements.txt"
  python3 -m pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Warning: OPENAI_API_KEY is not set. CrewAI may fail when calling the model."
fi

cd "${CREWAI_DIR}"
if [[ ! -f "crewai_openai_agents_bridge.py" ]]; then
  echo "Error: crewai_openai_agents_bridge.py not found in ${CREWAI_DIR}"
  exit 1
fi

echo ">>> Running CrewAI bridge for topic: ${TOPIC}"
python3 crewai_openai_agents_bridge.py "${TOPIC}"

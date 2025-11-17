# Multi-Agent Democratic Orchestrator

A TypeScript-based multi-agent orchestration system using democratic voting and specialized AI agents.

## Overview

This experimental project implements a democratic system where multiple specialized agents collaborate on tasks through voting and consensus building.

## Architecture

### Core Components

- **Architect Agent** - Maintains SRS, FEATURES, PROJECT_SUMMARY
- **Planner Agent** - Breaks features into actionable tasks  
- **Implementer Agent** - Writes code, markdown diffs
- **Reviewer Agent** - Flags hallucinations and drift
- **Memory Agent** - Summarizes lessons into long-term memory

### Orchestration

- Democratic voting system with scoring per role
- Base score per role, with Implementer and Architect weighted higher
- Penalties for hallucination and drift flags
- Highest scoring output treated as democratic winner

### Technology Stack

- **OpenRouter** - Primary LLM backend (free models)
- **Gemini** - Optional support via Google ADK A2A integration
- **Langfuse** - Rich observability and traces
- **Prometheus** - Metrics collection
- **LangGraph** - State graph orchestration with retries and branching

### Memory System

- Persistent semantic memory with short/long-term storage
- Tagged memory items with embeddings layer support
- Semantic recall capabilities

## Current Status

This is a canvas document containing the complete project structure. The file needs to be processed to extract individual TypeScript files and set up the proper project structure.

## Next Steps

1. Extract individual files from the canvas document
2. Set up proper TypeScript project structure
3. Install dependencies and configure environment
4. Implement Google ADK A2A adapter integration
5. Add semantic embeddings model and vector storage
6. Create full LangGraph implementation with retry/branching

## Development Notes

- Uses experimental multi-agent architecture
- Designed for extensibility and pluggable components
- Focus on democratic consensus rather than hierarchical control
- Rich observability and debugging capabilities
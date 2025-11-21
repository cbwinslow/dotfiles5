# OpenCode AI Agent Workflow System

## Overview
This document defines the comprehensive workflow and procedures for AI agents working on software development projects. It provides reusable patterns, templates, and guidelines that can be applied across different projects while maintaining project-specific separation.

## Core Principles

### 1. Separation of Concerns
- **Project-Specific**: Details specific to the current project
- **Agent-General**: Reusable workflows and patterns applicable to all projects
- **OpenCode-Specific**: Configuration and procedures specific to this OpenCode instance

### 2. Documentation Strategy
- **Living Documents**: All procedural documents are append-only
- **Cross-Reference**: Each document references others where appropriate
- **Version Control**: All documents include version information
- **Template Integration**: Documents include template sections where applicable

## Agent Workflow System

### Phase 1: Project Analysis & Planning
1. **Requirements Gathering**
   - Elicit comprehensive requirements from user
   - Clarify ambiguities through targeted questions
   - Document assumptions and constraints

2. **Architecture Design**
   - Define system architecture and components
   - Establish communication patterns between agents
   - Plan integration points and interfaces

3. **Technology Selection**
   - Research and recommend appropriate technologies
   - Consider performance, security, and maintainability
   - Document technology choices with rationale

### Phase 2: Implementation & Development
1. **Development Environment Setup**
   - Configure development tools and environments
   - Set up project structure and templates
   - Establish coding standards and practices

2. **Component Development**
   - Implement core functionality according to specifications
   - Follow established patterns and conventions
   - Maintain comprehensive documentation during development

3. **Integration & Testing**
   - Systematic integration testing of components
   - Performance testing and optimization
   - Security validation and penetration testing
   - User acceptance testing and feedback incorporation

### Phase 3: Deployment & Operations
1. **Production Preparation**
   - Finalize production configurations
   - Prepare deployment artifacts and documentation
   - Establish monitoring and alerting systems

2. **Deployment Execution**
   - Execute deployment procedures
   - Validate deployment success
   - Establish operational monitoring
   - Document deployment outcomes and lessons learned

### Phase 4: Maintenance & Evolution
1. **Continuous Improvement**
   - Monitor system performance and user feedback
   - Implement iterative improvements and optimizations
   - Update documentation based on operational experience
   - Plan future enhancements based on usage patterns

## Agent Communication Protocols

### Synchronous Communication
- **Request-Response Pattern**: Direct question-answer format
- **Status Updates**: Regular progress reporting
- **Error Handling**: Structured error reporting and escalation

### Asynchronous Communication
- **Event-Driven Architecture**: Loose coupling through event systems
- **Message Queuing**: Reliable message delivery guarantees
- **Timeout Management**: Appropriate timeout handling for long operations

## Quality Assurance Standards

### Code Quality
- **Review Process**: All code changes require review
- **Testing Coverage**: Minimum 90% test coverage required
- **Documentation**: All public APIs must be documented
- **Performance**: Performance benchmarks must be met
- **Security**: Security review for all changes

### Operational Excellence
- **Monitoring**: Comprehensive system monitoring
- **Alerting**: Proactive issue detection and notification
- **Recovery**: Automated recovery from failures
- **Scaling**: Handle increased load gracefully

## Template System

### Project Templates
- **README Template**: Standardized project README structure
- **Configuration Template**: Consistent configuration file formats
- **CI/CD Templates**: Reusable workflow definitions
- **Documentation Template**: Standardized documentation structure

### Decision Records
- **Architecture Decisions**: Record and justify architectural choices
- **Technology Selection**: Document technology selection rationale
- **Trade-off Analysis**: Document compromises and benefits
- **Rejection Rationale**: Record why alternatives were rejected

This workflow system ensures consistency, quality, and reusability across projects while allowing for project-specific customization and evolution.
# Contributing to YADM Dotfiles Configuration

## Overview

Thank you for your interest in contributing to this YADM dotfiles configuration project! This guide will help you get started with contributing effectively.

## Table of Contents

- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Updates](#documentation-updates)
- [Community Guidelines](#community-guidelines)

## Development Setup

### Prerequisites

Before contributing, ensure you have:

```bash
# Required tools
git --version  # 2.0+
ansible --version  # 2.14+
yadm --version    # 3.2.0+

# Optional but recommended
yamllint --version  # YAML linting
shellcheck --version  # Shell script validation
```

### Setting Up Development Environment

```bash
# 1. Fork the repository
gh repo fork cbwinslow/dotfiles5

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/dotfiles5.git
cd dotfiles5

# 3. Add upstream remote
git remote add upstream https://github.com/cbwinslow/dotfiles5.git

# 4. Create development branch
git checkout -b feature/your-feature-name

# 5. Set up YADM for development
yadm add ~/.config/yadm/config
yadm commit -m "feat: add development YADM config"
```

### Testing Your Changes

```bash
# Validate Ansible playbooks
./scripts/ansible-validate.sh

# Test shell configurations
shellcheck scripts/*.sh

# Check YAML syntax
yamllint ansible-environment/**/*.yml

# Dry run Ansible playbooks
ansible-playbook --check -i ansible-environment/inventory/hosts ansible-environment/playbooks/your-playbook.yml
```

## Contribution Guidelines

### Types of Contributions

We welcome the following types of contributions:

#### 🐛 Bug Fixes
- Fix broken functionality
- Resolve configuration issues
- Improve error handling

#### ✨ Features
- Add new Ansible playbooks
- Enhance automation scripts
- Add support for new tools

#### 📚 Documentation
- Improve README and guides
- Add missing examples
- Fix documentation errors

#### 🎨 Improvements
- Optimize performance
- Refactor code
- Improve security

#### 🧪 Testing
- Add new test cases
- Improve test coverage
- Fix test failures

### What to Contribute

#### High-Priority Contributions
1. **Security Issues**: Vulnerabilities, encryption problems
2. **Core Functionality**: Bootstrap, YADM, Ansible integration
3. **Documentation**: Critical gaps, outdated information

#### Medium-Priority Contributions
1. **New Playbooks**: Additional automation scenarios
2. **Tool Support**: New applications, languages
3. **Performance**: Optimization, resource usage

#### Low-Priority Contributions
1. **Cosmetic**: Typos, formatting
2. **Examples**: Additional use cases
3. **Minor Features**: Nice-to-have enhancements

### What NOT to Contribute

#### Out of Scope
1. **Personal Configurations**: User-specific settings
2. **Temporary Files**: Cache, logs, build artifacts
3. **Sensitive Data**: Personal keys, passwords
4. **Proprietary Tools**: Commercial software licenses

## Pull Request Process

### Before Submitting

#### 1. Create Issue (Optional but Recommended)
```bash
# Create issue for discussion
gh issue create \
  --title "Feature: Your Feature Name" \
  --body "Description of proposed changes and implementation approach"
```

#### 2. Prepare Your Branch
```bash
# Ensure branch is up to date
git fetch upstream
git rebase upstream/main

# Ensure clean working directory
git status
# Should be clean or have only your changes

# Test your changes
./scripts/ansible-validate.sh
```

#### 3. Submit Pull Request
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request
gh pr create \
  --title "feat: add your feature name" \
  --body "Description of changes and testing performed" \
  --base main \
  --head feature/your-feature-name
```

### Pull Request Template

Use this template for your pull requests:

```markdown
## Description
Brief description of changes and their purpose.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement
- [ ] Other (please specify)

## Testing
- [ ] Tested on fresh system
- [ ] Validated Ansible syntax
- [ ] Checked shell script compatibility
- [ ] Verified documentation accuracy

## Checklist
- [ ] Code follows project standards
- [ ] Self-reviewed the changes
- [ ] Updated relevant documentation
- [ ] Added tests for new functionality
- [ ] All tests pass
- [ ] No breaking changes without deprecation notice

## Additional Information
Any additional context, screenshots, or references.
```

## Code Standards

### Shell Scripts

#### Style Guidelines
```bash
# Use 4 spaces for indentation
# Use single quotes for strings unless expansion needed
# Use $(command) for command substitution
# Use [[ ]] for conditional tests
# Quote variables: "$variable"

# Good example
if [[ -f "$config_file" ]]; then
    source "$config_file"
fi

# Bad example
if [ -f $config_file ]; then
    source $config_file
fi
```

#### Error Handling
```bash
# Always use set -euo pipefail
set -euo pipefail

# Define error handling function
error_exit() {
    echo "Error: $1" >&2
    exit "${2:-1}"
}

# Use error handling
command_that_might_fail || error_exit "Command failed" 1
```

#### Documentation
```bash
# Add header with purpose
#!/bin/bash
# Script purpose and usage

# Add inline comments for complex logic
# Check if configuration exists and load it

# Use descriptive variable names
config_file="$HOME/.config/app/config"
```

### YAML Files

#### Style Guidelines
```yaml
# Use 2 spaces for indentation
# Use consistent key ordering
# Quote strings that contain special characters
# Use lists for collections
# Use proper YAML syntax

# Good example
---
tasks:
  - name: Install package
    package:
      name: "{{ package_name }}"
      state: present
    when: install_packages | default(false)

# Bad example
---
tasks:
- name: Install package
  package:
    name: "{{package_name}}"
    state: present
  when: install_packages|default(false)
```

#### Variable Naming
```yaml
# Use descriptive variable names
app_version: "1.2.3"
config_directory: "/opt/app"
enable_feature_x: true

# Use consistent naming convention
package_manager_enabled: true
docker_compose_version: "3.8"
```

### Ansible Playbooks

#### Structure Standards
```yaml
---
- name: Playbook Name
  hosts: localhost
  connection: local
  become: true
  vars_files:
    - ../group_vars/all.yml
  
  tasks:
    - name: Task name
      module_name:
        parameter: value
      when: condition
```

#### Task Guidelines
```yaml
# Use descriptive task names
- name: Install development tools
- name: Configure shell environment
- name: Set up AI agents

# Include proper error handling
- name: Install package with error handling
  block:
    - package:
        name: "{{ item }}"
        state: present
  rescue:
    - debug:
        msg: "Failed to install {{ item }}: {{ ansible_failed_result.msg }}"
  loop:
    - package1
    - package2
```

## Testing Requirements

### Unit Testing

#### Shell Scripts
```bash
# Test script functions
test_function() {
    # Setup test environment
    local test_file="/tmp/test_config"
    echo "test_value" > "$test_file"
    
    # Test function
    your_function "$test_file"
    
    # Verify result
    if [[ -f "$test_file" ]]; then
        echo "✓ Test passed"
        rm "$test_file"
    else
        echo "✗ Test failed"
        return 1
    fi
}

# Run tests
test_function
```

#### Ansible Playbooks
```bash
# Create test inventory
cat > test-inventory << 'EOF'
[test]
localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3
EOF

# Test playbook syntax
ansible-playbook --syntax-check -i test-inventory your-playbook.yml

# Dry run to check changes
ansible-playbook --check -i test-inventory your-playbook.yml
```

### Integration Testing

#### Full System Test
```bash
# 1. Set up test environment
mkdir -p /tmp/test-env
cd /tmp/test-env

# 2. Clone repository
git clone https://github.com/cbwinslow/dotfiles5.git

# 3. Run bootstrap
cd dotfiles5
./yadm-bootstrap.sh

# 4. Validate installation
./scripts/ansible-validate.sh

# 5. Test specific functionality
./scripts/ansible-install-apps.sh
```

## Documentation Updates

### When to Update Documentation

Update documentation when you:

1. **Add New Features**: Document new playbooks, scripts, or configuration options
2. **Change Behavior**: Update examples that no longer work
3. **Fix Issues**: Document solutions to common problems
4. **Deprecate Features**: Mark old features as deprecated with alternatives

### Documentation Standards

#### README Updates
```markdown
# Use clear, concise language
# Include installation prerequisites
# Provide quick start examples
# Add troubleshooting section
# Keep table of contents up to date
```

#### Code Comments
```yaml
# Add comments for complex logic
# Document variable purposes
# Explain conditional logic
# Provide usage examples

# Example
tasks:
  - name: Install development tools
    # Install essential development packages
    # Includes git, vim, curl, wget
    package:
      name: "{{ item }}"
      state: present
    loop:
      - git
      - vim
      - curl
      - wget
    when: install_dev_tools | default(true)
```

## Community Guidelines

### Code of Conduct

#### Be Respectful
- Welcome newcomers and help them learn
- Respect different viewpoints and experiences
- Focus on constructive feedback
- Assume good intentions

#### Be Collaborative
- Work together to solve problems
- Share knowledge and experience
- Consider impact of changes on all users
- Follow established consensus when possible

#### Be Professional
- Use inclusive language
- Provide constructive criticism
- Acknowledge and learn from mistakes
- Follow project standards and guidelines

### Communication Channels

#### GitHub
- **Issues**: [Create new issue](https://github.com/cbwinslow/dotfiles5/issues)
- **Discussions**: [Start discussion](https://github.com/cbwinslow/dotfiles5/discussions)
- **Pull Requests**: [Submit PR](https://github.com/cbwinslow/dotfiles5/pulls)

#### GitLab
- **Issues**: [Create issue](https://gitlab.com/cbwinslow/dotfiles5/-/issues)
- **Discussions**: [Start discussion](https://gitlab.com/cbwinslow/dotfiles5/-/issues)

### Recognition

Contributors will be recognized in:

1. **README.md**: Contributors section with GitHub usernames
2. **Release Notes**: Mention of significant contributions
3. **Git History**: Commit attribution with proper credit

## Release Process

### Version Management

```bash
# Use semantic versioning
MAJOR.MINOR.PATCH

# Examples:
1.0.0 - Initial release
1.1.0 - Feature addition
1.1.1 - Bug fix
2.0.0 - Major change
```

### Release Checklist

Before releasing:

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Security review completed
- [ ] Performance testing done

## Getting Help

### Resources

- [Project Documentation](README.md)
- [Usage Guide](docs/USAGE.md)
- [Examples](docs/EXAMPLES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

### Contact Maintainers

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and community discussion
- **Security Issues**: For sensitive security concerns only

---

**Thank you for contributing!** Every contribution helps make this project better for everyone.
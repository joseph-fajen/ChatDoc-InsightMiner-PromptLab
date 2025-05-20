# Contributing to ChatDoc-InsightMiner-PromptLab

Thank you for your interest in contributing to the ChatDoc-InsightMiner-PromptLab! This document provides guidelines and instructions for contributing to this project. Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Adding New Prompts](#adding-new-prompts)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Versioning](#versioning)

## Code of Conduct

This project is meant to be a welcoming and inclusive environment. All contributors are expected to:

- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what's best for the team and project
- Show empathy towards other team members

## Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/ChatDoc-InsightMiner-PromptLab.git
   cd ChatDoc-InsightMiner-PromptLab
   ```
   
   > Note: Replace `yourusername` with your actual GitHub username or organization name when you publish this repository.

2. **Set up your development environment**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env  # Add your API keys as needed
   ```

3. **Verify the setup**
   ```bash
   python scripts/toolkit.py setup
   ```

## Development Workflow

1. **Create a branch for your changes**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**
   - Write code that follows the project's coding standards
   - Add or update tests as necessary
   - Update documentation to reflect your changes

3. **Test your changes**
   ```bash
   python tests/run_tests.py
   ```

4. **Commit your changes with clear messages**
   ```bash
   git commit -m "Add feature: description of your feature"
   # or
   git commit -m "Fix: description of the issue you fixed"
   ```

## Submitting Changes

1. **Push your changes to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Submit a pull request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Explain the purpose and benefits of your changes

3. **Address review feedback**
   - Be responsive to comments and requested changes
   - Update your pull request as needed

## Coding Standards

- **Python Style**: Follow PEP 8 guidelines
- **Docstrings**: Use Google-style docstrings for functions and classes
- **Error Handling**: Include appropriate error handling with informative messages
- **Comments**: Write clear comments for complex logic
- **Naming Conventions**:
  - Use descriptive variable and function names
  - Classes: `CamelCase`
  - Functions and variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

## Adding New Prompts

When adding new prompt templates to the project:

1. **Choose the appropriate directory**:
   - `prompts/analysis_prompts/`: General analytical prompts
   - `prompts/creative_discovery_prompts/`: Exploratory and insight-generation prompts
   - `prompts/faq_prompts/`: Documentation-generation prompts
   - `prompts/prompt_for_specific_question/`: Targeted domain-specific prompts

2. **Follow the prompt template structure**:
   - Clear instructions at the beginning
   - Use the `{conversations}` placeholder where vector database content should be inserted
   - Include examples if helpful
   - End with specific output formatting instructions

3. **Test your prompt**:
   ```bash
   python scripts/toolkit.py analyze --prompt your_new_prompt.txt
   ```

4. **Document your prompt**:
   - Add a description to the README if it's a significant addition
   - Include comments within the prompt file explaining its purpose and expected output

## Testing Guidelines

- **Write tests for new functionality**:
  - Unit tests for individual functions
  - Integration tests for workflows

- **Test with representative data**:
  - Include sample data for testing if needed
  - Do not include sensitive or proprietary information

- **Verify compatibility**:
  - Test with at least one of the supported LLM providers
  - Ideally, test with all supported providers (OpenAI, Anthropic, Google Gemini)

## Documentation Guidelines

- **Keep README.md updated**:
  - Add new features to the feature list if significant
  - Update usage examples if interfaces change

- **Update QUICKSTART.md for workflow changes**:
  - Make sure quick start instructions remain accurate

- **Code Documentation**:
  - Document functions with docstrings
  - Explain parameters and return values
  - Note any side effects or important considerations

## Versioning

This project follows semantic versioning (SemVer):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Incompatible API changes
- **MINOR**: Added functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

When contributing, consider the impact of your changes on versioning.

---

Thank you for contributing to the ChatDoc-InsightMiner-PromptLab! Your efforts help make this tool better for everyone in our organization.
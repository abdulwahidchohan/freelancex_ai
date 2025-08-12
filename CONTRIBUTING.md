# Contributing to FreelanceX.AI 🤝

Thank you for your interest in contributing to FreelanceX.AI! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new features or improvements
- **📝 Documentation**: Improve docs, add examples, fix typos
- **💻 Code Contributions**: Submit pull requests with new features or bug fixes
- **🧪 Testing**: Help improve test coverage and quality
- **🌐 Translations**: Help translate the interface to other languages

### Before You Start

1. **Check existing issues** to avoid duplicates
2. **Read the documentation** to understand the project structure
3. **Set up your development environment** (see below)

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Local Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub first, then clone your fork
   git clone https://github.com/your-username/freelancex_ai.git
   cd freelancex_ai
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio flake8 black isort bandit
   ```

4. **Set up environment variables**
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys (at minimum, you need OPENAI_API_KEY)
   ```

5. **Verify setup**
   ```bash
   pytest test_*.py -v
   ```

## 📝 Code Style Guidelines

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 127 characters maximum
- **Import sorting**: Use `isort`
- **Code formatting**: Use `black`
- **Type hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code
black .
isort .

# Check code style
flake8 .

# Security checks
bandit -r .

# Run tests
pytest test_*.py -v
```

### Pre-commit Hooks

Consider setting up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow the `test_*.py` naming convention
- Use pytest fixtures for common setup
- Mock external API calls

### Test Structure

```python
import pytest
from your_module import your_function

def test_your_function_success_case():
    """Test successful execution of your_function."""
    result = your_function("test_input")
    assert result == "expected_output"

def test_your_function_error_case():
    """Test error handling of your_function."""
    with pytest.raises(ValueError):
        your_function("invalid_input")
```

### Running Tests

```bash
# Run all tests
pytest test_*.py -v

# Run specific test file
pytest test_agentic_ai.py -v

# Run with coverage
pytest test_*.py --cov=. --cov-report=html
```

## 🔄 Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   pytest test_*.py -v
   ```

2. **Check code style**
   ```bash
   black . --check
   isort . --check-only
   flake8 .
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### Pull Request Guidelines

1. **Create a descriptive title** that summarizes the change
2. **Write a detailed description** explaining:
   - What the change does
   - Why it's needed
   - How it was implemented
   - Any breaking changes

3. **Reference related issues** using keywords like "Fixes #123" or "Closes #456"

4. **Include screenshots** for UI changes

5. **Update documentation** if the change affects user-facing features

### Example Pull Request

```markdown
## Description
Adds support for Google Gemini API as an alternative to OpenAI.

## Changes
- Added `google-generativeai` dependency
- Created `fx_agents/api_provider.py` for multi-provider support
- Updated configuration to support API provider selection
- Added fallback mechanism when primary provider fails

## Testing
- Added tests for API provider switching
- Verified fallback functionality
- Tested with both OpenAI and Gemini APIs

## Breaking Changes
None - this is a backward-compatible enhancement.

Fixes #123
```

## 🐛 Bug Reports

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Try to reproduce** the issue consistently
3. **Check the documentation** for known solutions

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Windows 10, macOS 12.0]
- Python Version: [e.g. 3.9.7]
- FreelanceX.AI Version: [e.g. 1.0.0]

## Additional Information
- Screenshots if applicable
- Error messages
- Log files
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Brief description of the feature you'd like to see.

## Use Case
Explain why this feature would be useful.

## Proposed Implementation
If you have ideas for implementation, share them here.

## Alternatives Considered
Any alternative solutions you've considered.

## Additional Information
Any other relevant information.
```

## 📚 Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up to date
- Use proper markdown formatting
- Include screenshots for UI features

### Documentation Structure

- **README.md**: Project overview and quick start
- **API_CONFIGURATION_GUIDE.md**: Detailed API setup
- **ARCHITECTURE.md**: System architecture
- **CONTRIBUTING.md**: This file
- **Code comments**: Inline documentation

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community
- Show empathy towards other community members

### Communication

- Use clear, respectful language
- Provide constructive feedback
- Ask questions when you need clarification
- Help others when you can

## 📞 Getting Help

If you need help with contributing:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Create a new issue** with the "question" label
4. **Join discussions** in GitHub Discussions

## 🎉 Recognition

Contributors will be recognized in:

- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to FreelanceX.AI! 🚀

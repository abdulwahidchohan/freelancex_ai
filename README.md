# FreelanceX.AI 🤖

> **Enhanced AI-Powered Freelance Assistant with OpenAI Agents SDK Integration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI%20Agents%20SDK-Latest-green.svg)](https://openai.github.io/openai-agents-python/)
[![Chainlit](https://img.shields.io/badge/Chainlit-2.6+-purple.svg)](https://chainlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-red.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [🚀 Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [📦 Installation](#-installation)
- [⚡ Quick Start](#-quick-start)
- [🔧 Configuration](#-configuration)
- [📚 Usage Examples](#-usage-examples)
- [🤖 Agent System](#-agent-system)
- [🔌 API Integration](#-api-integration)
- [🧪 Testing](#-testing)
- [📖 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## Overview

FreelanceX.AI is a comprehensive AI-powered platform designed to assist freelancers with every aspect of their business. Built with the latest **OpenAI Agents SDK**, it provides intelligent automation for job searching, proposal writing, financial calculations, market research, and more.

### 🎯 Mission
Empower freelancers with AI-driven tools to streamline their workflow, increase productivity, and achieve better business outcomes through intelligent automation and personalized assistance.

## 🚀 Key Features

### 🤖 **Enhanced Agent System**
- **10+ Specialized AI Agents** with OpenAI Agents SDK integration
- **Dynamic Agent Routing** with intelligent handoffs
- **Real-time Context Management** with enhanced memory
- **Multi-API Support** (OpenAI, Google Gemini, Anthropic) with automatic fallback

### 💼 **Freelance Business Tools**
- **Smart Job Search** - AI-powered opportunity discovery
- **Proposal Writer** - Professional proposal generation
- **Financial Calculator** - Budget, tax, and ROI analysis
- **Market Research** - Comprehensive market insights
- **Client Management** - Relationship optimization
- **Security & Compliance** - Data protection and audit trails

### 🔧 **Technical Excellence**
- **Full SDK Integration** - Leveraging OpenAI Agents SDK features
- **Guardrails & Validation** - Input/output safety checks
- **Tracing & Monitoring** - Comprehensive debugging and analytics
- **Session Management** - Persistent context and memory
- **Error Handling** - Robust error recovery and fallback strategies

## 🏗️ Architecture

```
FreelanceX.AI
├── 🤖 Agent Layer (OpenAI Agents SDK)
│   ├── Executive Core (Strategy & Governance)
│   ├── Cognitive Core (Reasoning & Learning)
│   ├── Operations (Job Search, Proposals, etc.)
│   ├── Security (Compliance & Protection)
│   └── Expansion (Growth & Innovation)
├── 🔌 API Layer (FastAPI)
│   ├── Authentication & Authorization
│   ├── Memory Management
│   └── Multi-Provider Support
├── 🎨 Frontend (Chainlit)
│   ├── Chat Interface
│   ├── Rich Responses
│   └── File Uploads
└── 🗄️ Data Layer (SQLite)
    ├── Session Storage
    ├── Memory Management
    └── Performance Analytics
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key (or Google Gemini/Anthropic)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/freelancex_ai.git
cd freelancex_ai
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## ⚡ Quick Start

### Start the Application
```bash
# Start the Chainlit frontend
chainlit run chainlit_app/main.py

# Or start the FastAPI backend
python api_gateway.py
```

### First Interaction
1. Open your browser to `http://localhost:8000`
2. Ask: *"Help me find freelance Python development jobs"*
3. Watch the AI agents work together to find opportunities!

## 🔧 Configuration

### Environment Variables
```bash
# Required API Keys (at least one)
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-anthropic-key

# Optional Configuration
FREELANCEX_SESSION_SECRET=your-session-secret
FREELANCEX_LOG_LEVEL=INFO
FREELANCEX_ENABLE_TRACING=true
```

### Agent Configuration
```python
from config.settings import get_config

config = get_config()
# Customize agent behavior, API settings, and more
```

## 📚 Usage Examples

### Job Search
```python
from fx_agents import triage_agent

# Find Python development opportunities
result = await triage_agent.route_request(
    "Find remote Python development jobs with $50-100/hour rates"
)
```

### Proposal Writing
```python
# Generate professional proposal
result = await triage_agent.route_request(
    "Write a proposal for a web development project: E-commerce site, 3 months, $15k budget"
)
```

### Financial Analysis
```python
# Calculate project budget and ROI
result = await triage_agent.route_request(
    "Calculate budget for a 40-hour project at $75/hour with 20% profit margin"
)
```

## 🤖 Agent System

### Core Agents

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| **Executive Agent** | Strategic decision-making | Business analysis, performance evaluation |
| **Cognitive Agent** | Deep reasoning | Problem-solving, knowledge synthesis |
| **Job Search Agent** | Opportunity discovery | Market analysis, job matching |
| **Proposal Writer** | Professional proposals | Custom writing, pricing strategies |
| **Math Agent** | Financial calculations | Budgeting, tax analysis, ROI |
| **Web Research Agent** | Market intelligence | Competitive analysis, trends |
| **Marketing Agent** | Growth strategies | Campaign design, audience targeting |
| **Security Agent** | Data protection | Compliance, risk assessment |
| **UX Agent** | User experience | Interface optimization, feedback analysis |
| **Expansion Agent** | Business growth | Market opportunities, partnerships |

### Agent Handoffs
The system uses intelligent routing to delegate tasks to the most appropriate agent:

```python
# Example: Complex request automatically routed
user_request = "I need help finding Python jobs, writing a proposal, and calculating my rates"
# → Triage Agent analyzes and routes to:
#   1. Job Search Agent (find opportunities)
#   2. Proposal Writer (create proposal)
#   3. Math Agent (calculate optimal rates)
```

## 🔌 API Integration

### REST API Endpoints
```bash
# Authentication
POST /auth/login
POST /auth/register

# Agent Operations
POST /api/route-request
GET /api/agent-status
GET /api/memory/{session_id}

# System Management
GET /api/health
GET /api/providers
```

### SDK Integration
```python
from fx_agents import triage_agent, get_api_manager

# Use the enhanced agent system
api_manager = get_api_manager()
result = await triage_agent.route_request(
    message="Your request here",
    session_id="unique-session-id",
    user_id="user-123"
)
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/
```

### Test Specific Components
```bash
# Test agent system
python -c "from fx_agents import triage_agent; print('✅ Agents loaded successfully!')"

# Test API integration
python -c "from fx_agents.api_provider import get_api_manager; print('✅ API ready!')"
```

### Performance Testing
```bash
# Load testing with multiple concurrent requests
python tests/performance_test.py
```

## 📖 Documentation

### 📚 Comprehensive Guides
- **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- **[API Documentation](docs/api.md)** - Complete API reference
- **[Agent Development](docs/agents.md)** - How to create custom agents
- **[Deployment Guide](docs/deployment.md)** - Production deployment

### 🎥 Video Tutorials
- [Getting Started with FreelanceX.AI](https://youtube.com/watch?v=example)
- [Building Custom Agents](https://youtube.com/watch?v=example)
- [Advanced Configuration](https://youtube.com/watch?v=example)

### 📖 Examples
- [Basic Usage Examples](examples/basic_usage.py)
- [Advanced Agent Patterns](examples/advanced_patterns.py)
- [Integration Examples](examples/integrations.py)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone
git clone https://github.com/yourusername/freelancex_ai.git
cd freelancex_ai

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Submit pull request
```

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Use type hints throughout

## 🏆 Acknowledgments

- **OpenAI** for the Agents SDK and GPT models
- **Chainlit** for the excellent chat interface
- **FastAPI** for the robust API framework
- **Pydantic** for data validation and serialization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [docs.freelancex.ai](https://docs.freelancex.ai)
- **Issues**: [GitHub Issues](https://github.com/yourusername/freelancex_ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/freelancex_ai/discussions)
- **Email**: support@freelancex.ai

---

**Made with ❤️ for the freelance community**

*FreelanceX.AI - Empowering freelancers with AI-driven tools for success.*

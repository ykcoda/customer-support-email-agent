# Customer Support Email Agent

A LandGraph-based customer support email agent built with Python 3.12, FastAPI, LangChain, and OpenAI.

## Overview

This project implements an intelligent email agent that:
- Receives customer support emails
- Classifies and prioritizes requests
- Generates contextual responses using LLMs
- Manages conversation state with LandGraph
- Integrates with FastAPI for HTTP APIs

## Technology Stack

- **Python 3.12** - Core language
- **FastAPI** - Web framework
- **LandGraph** - Agent workflow orchestration
- **LangChain** - LLM framework
- **OpenAI** - Language model provider
- **Pydantic** - Data validation

## Project Structure

```
src/
├── api/               # FastAPI application
│   └── routes/        # API endpoints
├── graph/             # LandGraph workflow definitions
│   └── nodes/         # Graph nodes for email processing
├── services/          # Business logic services
├── schemas/           # Pydantic data models
├── prompts/           # LLM prompt templates
├── core/              # Core configuration
└── utils/             # Utility functions

data/
├── knowledge_base/    # FAQs and documentation
└── examples/          # Example data

tests/                 # Test suite
├── unit/
└── integration/
```

## Setup

### Prerequisites
- Python 3.12+
- [`uv` package manager](https://docs.astral.sh/uv/getting-started/)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd customer-support-email-agent
```

2. Sync dependencies (creates virtual env and installs):
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Run the application:
```bash
uv run uvicorn src.api.main:app --reload
```

### Using uv

```bash
# Sync dependencies
uv sync

# Run a command
uv run uvicorn src.api.main:app --reload

# Run Python script
uv run python script.py

# Run tests
uv run pytest tests/

# Add a dependency
uv add package_name

# Add dev dependency
uv add --dev package_name
```

## Configuration

All configuration is managed through environment variables in `.env`:

- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - Model to use (default: gpt-4)
- `API_PORT` - FastAPI server port (default: 8000)
- `EMAIL_PROVIDER` - Email provider (smtp, mailgun, sendgrid)
- `KNOWLEDGE_BASE_PATH` - Path to knowledge base files

## Development

### Running Tests
```bash
uv run pytest tests/
```

### Code Quality
```bash
# Format code
uv run black src/

# Lint
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Virtual Environment
```bash
# Activate venv (created by uv sync)
source .venv/bin/activate

# Or use uv to run commands without activating
uv run command_here
```

## Project Status

This is a scaffold for the LandGraph customer support email agent. Core functionality is in development.

## License

MIT

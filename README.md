# Video Generation Analysis
Automated video generation and publishing with continuous, real-time engagement analytics.

Built with modern Python tools like Poetry, Ruff, Pytest to ensure stability, performance, and maintainability.

---

## Features Overview

- **Automated Generation** — AI video generation based off keywords, analysis of keywords creating most engagement.
- **Scheduled Publishing** — Publish seamlessly to platforms YouTube, (TODO Tiktok, Instagram) via APIs.
- **Real-Time Analytics** — Pull engagement data (views, likes, comments) of published views and analyse to generate videos similar to best performers.
- **Quality Assurance** — Enforce clean, type-safe code with Ruff and Mypy integration.

---
## Installation Guide

The following steps will help you set up **Video Generation Analysis** using **Poetry** for dependency management.

> **Note:** This project requires **Python 3.11** or newer.

### 1. Prerequisites

Before installing the project, ensure the following tools are installed:

- **Python 3.11+** — [Download here](https://www.python.org/downloads/)
- **Poetry** — Used for packaging and dependency management. [Installation guide](https://python-poetry.org/docs/#installation)

### 2. Setup

Clone the repository and install dependencies using Poetry.

**a. Clone the Repository**

```bash
git clone https://github.com/tomcmead/video-generation-analysis.git
cd video-generation-analysis
```

**b. Install Dependencies with Poetry**

This command reads pyproject.toml, creates a virtual environment, and installs all main and development dependencies.

```bash
poetry install
poetry install --with-docs
```

### 3. Environment Variables

To enable video publishing and analysis features, configure the required environment variables.

Create a `.env` file in the project root based on `.env.example` (`.env` already ignored by `.gitignore`):

Example `.env`:

```bash
GEMINI_API_KEY=<gemini-api-key>
YOUTUBE_CLIENT_SECRETS_FILE=<youtube-api-client-json>
```

### 4. Run the Application

Run the project’s main entry point within Poetry’s environment:

```bash
poetry run python video_generation_analysis/main.py --prompt "initial video generation prompt"
```

### 5. Development Commands

**Run tests:**
`poetry run pytest`

**Static type checking:**
`poetry run mypy video_generation_analysis`

**Format and lint code:**
`poetry run ruff format .`

**Build distributable files (`.whl` and `.tar.gz`):**
`poetry build`

**Generate documentation:**
`poetry run sphinx-apidoc -f -o docs/source/api ./video_generation_analysis ./tests/* --separate --module-first`
`poetry run sphinx-build -E -b html docs/source docs/_build`

**Pre-commit hooks install:**
`poetry add --group dev pre-commit`
`poetry run pre-commit install`
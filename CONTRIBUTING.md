# Contributing to AI Learning Assistant

Thank you for your interest in contributing! This document outlines the process for contributing to this project.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI-Learning-Assistant.git
   cd AI-Learning-Assistant
   ```
3. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your API keys
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Code Standards

### Python (Backend)
- Follow **PEP 8** style guidelines
- Add docstrings to all public functions and classes
- Use type hints for function signatures
- Keep functions focused — single responsibility
- Log errors with `logger.error()`, not `print()`

### JavaScript (Frontend)
- Use functional React components with hooks
- Keep components small and focused
- Handle loading and error states explicitly
- No inline styles — use the CSS class system in `global.css`

## Pull Request Process

1. Ensure your branch is up to date with `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
2. **Test your changes** — run the backend and verify all endpoints work
3. **Build the frontend** — `npm run build` must succeed without errors
4. Write a clear PR description explaining:
   - What problem does this solve?
   - What changes were made?
   - How was it tested?
5. Reference any related issues with `Closes #123`

## Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) issue template.

Include:
- Steps to reproduce
- Expected vs actual behaviour
- Environment (OS, Python version, Node version)
- Any relevant logs or error messages

## Suggesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold this code.

## Questions?

Open a [Discussion](https://github.com/Shreya15err2/AI-Learning-Assistant/discussions) or comment on an existing issue.

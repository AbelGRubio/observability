# Contributing to Backend DAS Device

Thank you for your interest in contributing to **Backend DAS Device** 🎉
This document describes how to set up your development environment, follow the code style, run tests, and submit merge requests.

---

## 🧰 Development Environment Setup

1. **Clone the repository**

   ```bash
   git clone https://gitlab.com/your-org/backend-das-device.git
   cd backend-das-device
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**

   Copy the `.env.example` file to `.env` and update with your local values:

   ```bash
   cp .env.example .env
   ```

---

## 🧪 Running Tests

Run all unit and integration tests before submitting code:

```bash
pytest --cov=src tests/
```

> Include tests for any new feature or bug fix you add.

For load testing (optional):

```bash
cd load_tests
locust -f locustfile.py --host http://localhost:8000
```

---

## 🧹 Code Style and Formatting

This project follows **PEP8** and **type hints**.

### Code style tools:
- **black** – automatic code formatting
- **ruff** – linting
- **mypy** – type checking

Run checks locally before committing:

```bash
black src tests
ruff check src tests
mypy src
```

> A pre-commit hook configuration is provided to automate these checks.

To install the hooks:

```bash
pre-commit install
```

---

## 🌿 Branch Naming Convention

Use descriptive branch names:
```
feature/<short-description>
fix/<issue-id>-<short-description>
chore/<task-name>
```

Example:
```
feature/add-device-endpoint
fix/123-websocket-error
```

---

## 💬 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard:

```
<type>(scope): <short summary>
```

Types include: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

Examples:
```
feat(api): add endpoint for device status
fix(websocket): handle disconnection gracefully
```

---

## 🔀 Merge Requests

1. Fork the repository (if external).
2. Create a feature branch.
3. Push your changes.
4. Open a **Merge Request (MR)** targeting the `develop` branch.
5. Ensure all pipelines pass (CI/CD, linting, tests).
6. Request a review from a maintainer.

---

## 📦 Dependencies

All dependencies must be declared in `requirements.txt`.
For new libraries, ensure they are compatible with Python 3.10+ and approved for production use.

---

## 🧑‍💻 Code of Conduct

Please be respectful and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
We encourage collaboration, constructive feedback, and inclusivity.

---

## 💡 Tips

- Keep commits small and focused.
- Write docstrings for new functions and classes.
- Update README.md or API documentation if necessary.
- Test thoroughly before opening a merge request.

---

Thank you for helping improve **Backend DAS Device** 🚀

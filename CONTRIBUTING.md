# Contributing Guide

Thank you for your interest in contributing to the **Welfare Fraud Detection System**.

We welcome contributions that improve the project, whether it is fixing bugs, improving documentation, or adding new features.

---

# Project Setup

## 1. Clone the Repository

```bash
git clone https://github.com/AryanKumarOfficial/welfare-fraud-detection-system
cd welfare-fraud-detection-system
```

---

## 2. Install Dependencies

Use the Makefile to install all required dependencies.

```bash
make setup
```

This will:

- Install Bun workspace dependencies
- Create the Python virtual environment
- Install ML dependencies

---

## 3. Run Development Environment

```bash
make dev
```

This will start:

| Service         | Port |
| --------------- | ---- |
| Admin Dashboard | 3000 |
| API Server      | 3001 |
| ML Service      | 8000 |
| PostgreSQL      | 5432 |
| Redis           | 6379 |

---

# Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit your changes
5. Push the branch
6. Open a Pull Request

Example:

```bash
git checkout -b feature/add-fraud-api
```

---

# Commit Message Guidelines

Please use clear and descriptive commit messages.

Format:

```
<type>: <description>
```

Examples:

```
feat: add fraud detection API endpoint
fix: resolve authentication bug
docs: update README setup instructions
chore: add docker configuration
```

---

# Code Guidelines

## General

- Keep code clean and modular.
- Follow existing project structure.
- Write readable and maintainable code.

## Frontend

- Use TypeScript.
- Follow Next.js best practices.
- Keep components reusable.

## Backend

- Use clear API structures.
- Validate incoming data.
- Follow REST API design principles.

## ML Service

- Keep model logic separate from API logic.
- Document preprocessing and feature engineering steps.
- Ensure reproducibility of models.

---

# Reporting Issues

If you encounter a bug or want to request a feature:

1. Open a GitHub Issue
2. Provide a clear description
3. Include steps to reproduce if applicable

---

# Pull Request Guidelines

Before submitting a pull request:

- Ensure the code compiles and runs.
- Test your changes locally.
- Keep pull requests focused and small.

Pull Requests should include:

- Clear description of changes
- Related issue reference (if applicable)
- Screenshots or logs if needed

---

# Community

Please follow the project's [**Code of Conduct**](./CODE_OF_CONDUCT.md) when interacting with others.

We value respectful and constructive collaboration.

---

# License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

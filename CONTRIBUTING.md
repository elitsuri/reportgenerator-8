# Contributing to Reportgenerator 5

Thank you for your interest in contributing.

*Updated: 2026-04-06*

---

## Development Setup

```bash
git clone <repository-url>
cd reportgenerator-5
cp .env.example .env
# Fill in your local values in .env
```

See README.md for stack-specific installation instructions.

## Branching Strategy

| Branch      | Purpose                                     |
|-------------|---------------------------------------------|
| `main`      | Stable, production-ready code               |
| `develop`   | Integration branch for upcoming release     |
| `feature/*` | New features — branch from `develop`        |
| `fix/*`     | Bug fixes — branch from `main` or `develop` |
| `chore/*`   | Refactoring, dependency updates             |

```bash
git checkout -b feature/my-feature develop
```

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

**Examples:**
```
feat(api): add pagination to /users endpoint
fix(auth): resolve token refresh race condition
docs: update API reference for v1.2
chore(deps): upgrade dependencies to latest stable
ci: add coverage reporting to CI pipeline
```

## Pull Request Process

1. Ensure all tests pass locally
2. Update documentation if public interfaces changed
3. Add tests for new functionality (coverage must not decrease)
4. Fill in the PR description completely
5. Request review from a maintainer

## Code Standards

- Keep functions focused and small
- Write self-documenting variable and function names
- Add comments for non-obvious logic only
- Prefer explicit over implicit
- Match the existing code style in the file you are editing

## Reporting Issues

Open an issue with:
- A clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behavior
- Environment (OS, runtime version, relevant config)

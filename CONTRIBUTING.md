# Contributing to Antigravity Reader

Thank you for considering contributing to Antigravity Reader!

## Development Workflow

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Run the test suite:
   ```bash
   make test
   ```

3. Ensure no external runtime dependencies are introduced to keep the core lightweight and portable.

4. Commit your changes with clear, semantic commit messages:
   ```bash
   git commit -m "feat: add support for custom themes"
   ```

5. Push to your branch and submit a Pull Request.

## Code Standards
- Keep Python code PEP-8 compliant.
- Maintain backwards compatibility with Python 3.8+.
- Do not add external runtime libraries unless strictly necessary.

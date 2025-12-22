# Contributing to Remora Freqtrade Integration

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, Freqtrade version, etc.)
- Error messages or logs (if applicable)

### Suggesting Features

Feature suggestions are welcome! Open an issue describing:

- The feature you'd like to see
- Why it would be useful
- How it might work

### Submitting Code

1. **Fork the repository**

2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the code style:
   - Use clear, descriptive variable names
   - Add docstrings to functions and classes
   - Include comments for complex logic
   - Follow PEP 8 style guidelines

4. **Add tests** if applicable (especially for new features)

5. **Update documentation** if you've changed functionality

6. **Test your changes**:
   ```bash
   # Run tests
   pytest tests/
   
   # Test with a strategy
   freqtrade backtesting --strategy YourStrategy
   ```

7. **Commit your changes** with clear commit messages:
   ```bash
   git commit -m "Add: description of your change"
   ```

8. **Push and create a Pull Request**

## Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings to public functions/classes

## Strategy Contributions

If you're contributing a new strategy:

- Include clear docstrings explaining the strategy logic
- Add comments for Remora integration points
- Test with backtests before submitting
- Consider adding it to the examples section

## Testing

- Write tests for new features
- Ensure existing tests still pass
- Test with real Freqtrade backtests when possible

## Documentation

- Update README.md if adding major features
- Add examples for new patterns
- Keep integration guide up to date

## Questions?

Open an issue or reach out via https://remora-ai.com/

Thank you for contributing! 🎉





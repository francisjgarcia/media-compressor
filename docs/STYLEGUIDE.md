# Coding Style Guide

This document outlines the coding standards and conventions for this project. Follow these guidelines to ensure consistency and quality in Python code.

## General Guidelines

### Indentation

- **Style**: Use spaces instead of tabs.
- **Indentation Size**:
  - **Python Files (`*.py`)**: Use 4 spaces for indentation.

### Line Endings and Encoding

- **Line Endings**: Use Unix-style line endings (`LF`).
- **Encoding**: Use UTF-8 encoding for files.

### Whitespace and Final Newline

- **Trim Trailing Whitespace**: Remove trailing whitespace from lines.
- **Insert Final Newline**: Ensure each file ends with a newline.

## Formatting and Style Tools

To maintain consistent code formatting in Python, use the following tools:

### Black

- **Description**: Black is a code formatter for Python that enforces a uniform style.
- **Installation**: `pip install black`
- **Usage**: Run `black filename.py` to format a file.

### autopep8

- **Description**: autopep8 formats Python code to comply with PEP 8 style guide.
- **Installation**: `pip install autopep8`
- **Usage**: Run `autopep8 filename.py` to format a file.

### YAPF (Yet Another Python Formatter)

- **Description**: YAPF is a flexible formatter that adheres to PEP 8 guidelines.
- **Installation**: `pip install yapf`
- **Usage**: Run `yapf -i filename.py` to format a file.

### Flake8

- **Description**: Flake8 combines Pyflakes for error detection and pep8 for style checking.
- **Installation**: `pip install flake8`
- **Usage**: Run `flake8 filename.py` to check the code.

## Python Code Examples

### Good Example

```python
def calculate_total(items):
    total = sum(item['price'] for item in items)
    return total


def format_item(item):
    return f"{item['name']}: ${item['price']:.2f}"
```

### Bad Example

```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total

def format_item(item):
    return '{}: ${:.2f}'.format(item['name'], item['price'])
```

## Conventional Commits

For commit messages, follow the [Conventional Commits](https://www.conventionalcommits.org) standard, which establishes a clear and structured format. This approach improves the readability of the change history and allows automated tools to identify versions, generate release notes, and more.

```bash
<type>[optional scope]: <description>
```

Where:

- `type`: Indicates the category of the change. Common values include:
feat: A new feature.
  - `feat`: Adds a new feature to the project.
  - `fix`: A bug fix.
  - `docs`: Documentation-only changes.
  - `style`: Formatting changes (without affecting logic).
  - `refactor`: Code changes that neither fix a bug nor add a feature.
  - `perf`: To improve performance.
  - `test`: Adding or updating tests.
  - `ci`: Changes to CI/CD configuration files or scripts.
  - `chore`: Maintenance tasks (e.g., dependency updates).
  - `revert`: Reverting a previous commit.
  - `wip`: Work in progress and not ready to be merged.
  - `hotfix`: Urgent fixes for critical issues that need immediate resolution.
  - `breaking`: Changes that break compatibility with previous versions.
- `scope`: Optional, and can specify the part of the project the change affects (e.g., ui, api, database).
- `description`: Briefly explains the purpose of the commit.

## Commit Examples

Example of a commit for a new feature:
```bash
feat(api): add user authentication endpoint
```

Example of a commit to fix a bug:
```bash
fix(ui): correct button alignment issue on mobile
```

Example of a commit for documentation changes:
```bash
docs(readme): update installation instructions
```

## Extended Messages
You can add a more detailed description if necessary, separating the title from the body with a blank line:

```bash
fix(database): resolve connection timeout issue

The connection timeout was occurring due to a misconfigured retry policy. Updated the retry logic to improve stability.
```

Following this format for commits ensures consistent structure and allows for better traceability of changes within the project.


## Conclusion

By following these guidelines, we can maintain clean, consistent, and maintainable Python code. If you have any questions about these standards or need more details, please contact the project maintainers.

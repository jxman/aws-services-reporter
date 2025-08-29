# AWS Services Reporter - Development Guide

## Pre-commit Hooks Setup

Pre-commit hooks automatically format your code and check for issues before each commit, preventing CI/CD failures.

### Quick Setup

```bash
# 1. Install development dependencies (includes pre-commit)
pip install -r requirements-dev.txt

# 2. Install pre-commit hooks
pre-commit install

# 3. Test the hooks
pre-commit run --all-files
```

### What the Hooks Do

The pre-commit configuration includes:

1. **Black Formatting**: Automatically formats Python code to consistent style
2. **Isort**: Organizes imports in alphabetical order
3. **Trailing Whitespace**: Removes unnecessary spaces at end of lines
4. **End-of-file Fixer**: Ensures all files end with a newline
5. **Merge Conflicts**: Checks for Git merge conflict markers
6. **YAML Check**: Validates YAML file syntax
7. **Python AST**: Checks for Python syntax errors

### How It Works

```bash
# Every time you commit, pre-commit runs automatically:
git add .
git commit -m "your message"  # <- hooks run here automatically

# If hooks find issues, they'll either:
# 1. Fix them automatically (formatting)
# 2. Stop the commit and show errors

# After auto-fixes, re-add and commit:
git add .
git commit -m "your message"  # <- now it should pass
```

### Manual Hook Execution

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run hooks on specific files
pre-commit run --files path/to/file.py

# Run only specific hooks
pre-commit run black --all-files
pre-commit run isort --all-files

# Skip hooks for emergency commits (NOT RECOMMENDED)
git commit -m "emergency fix" --no-verify
```

### Development Workflow

**Recommended daily workflow:**

```bash
# 1. Make your changes
vim aws_services_reporter/some_file.py

# 2. Test your changes
python -m pytest tests/ -v

# 3. Commit (hooks run automatically)
git add .
git commit -m "fix: improve error handling"

# 4. If hooks fix formatting, re-commit
git add .
git commit -m "fix: improve error handling"
```

### Configuration Details

The `.pre-commit-config.yaml` file defines which hooks run:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-ast
```

## IDE Integration

### VS Code Setup

Create `.vscode/settings.json`:

```json
{
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.sortImports.args": ["--profile", "black"],
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### PyCharm Setup

1. Go to **Settings → Tools → External Tools**
2. Add Black formatter:
   - **Name**: Black
   - **Program**: `black`
   - **Arguments**: `$FilePath$`
   - **Working directory**: `$ProjectFileDir$`

## Troubleshooting

### Common Issues

**Issue**: `pre-commit command not found`
```bash
# Solution: Install in virtual environment
source .venv/bin/activate
pip install pre-commit
pre-commit install
```

**Issue**: Hooks are too slow
```bash
# Solution: Update hooks to latest versions
pre-commit autoupdate

# Or skip slow hooks in emergencies
git commit --no-verify -m "emergency commit"
```

**Issue**: Import sorting conflicts
```bash
# Solution: Use black-compatible isort profile
isort --profile=black .
```

### Updating Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Reinstall hooks after updates
pre-commit install --install-hooks
```

### Disabling Hooks

```bash
# Temporarily skip all hooks
git commit --no-verify -m "skip hooks"

# Disable specific hooks in .pre-commit-config.yaml
# Add 'exclude:' patterns or comment out repos
```

## Benefits

### Why Use Pre-commit Hooks?

1. **Prevents CI/CD Failures**: Catches formatting issues before push
2. **Consistent Code Style**: All team members use same formatting
3. **Saves Time**: No manual formatting needed
4. **Fewer Merge Conflicts**: Consistent style reduces conflicts
5. **Better Code Quality**: Catches syntax errors early

### Before/After Comparison

**Without Pre-commit Hooks:**
```bash
# Developer workflow
git add .
git commit -m "fix bug"
git push
# CI fails due to formatting
# Fix formatting manually
git add .
git commit -m "fix formatting"
git push
# Finally passes CI
```

**With Pre-commit Hooks:**
```bash
# Developer workflow  
git add .
git commit -m "fix bug"
# Hooks auto-format and check code
git add .
git commit -m "fix bug"
git push
# CI passes immediately
```

## Team Guidelines

### For New Contributors

1. **Always install pre-commit hooks first**
2. **Run `pre-commit run --all-files` before first commit**
3. **Don't use `--no-verify` unless emergency**
4. **Update hooks regularly with `pre-commit autoupdate`**

### For Code Reviews

- ✅ **Accept**: Auto-formatted code from pre-commit hooks
- ❌ **Request changes**: Manual formatting that differs from black/isort
- ✅ **Merge**: PRs that pass all pre-commit checks
- ⚠️ **Question**: Commits with `--no-verify` (should be rare)

This setup ensures consistent, high-quality code across all contributions to the AWS Services Reporter project.

Contributing to AWS Services Reporter
====================================

We welcome contributions to AWS Services Reporter! This guide covers everything you need to know to contribute effectively to the project.

Getting Started
---------------

**Prerequisites:**

- Python 3.8 or higher
- Git for version control
- AWS CLI configured for testing
- Familiarity with Python development practices

**Development Setup:**

1. **Fork and clone the repository**:

   .. code-block:: bash

      git clone https://github.com/your-username/aws-services-reporter.git
      cd aws-services-reporter

2. **Create virtual environment**:

   .. code-block:: bash

      python3 -m venv .venv
      source .venv/bin/activate  # Linux/Mac

3. **Install development dependencies**:

   .. code-block:: bash

      pip install -r requirements-dev.txt

4. **Install pre-commit hooks**:

   .. code-block:: bash

      pre-commit install

Development Workflow
--------------------

**Branch Strategy:**

- ``main`` - Production-ready code
- ``develop`` - Integration branch for new features
- ``feature/feature-name`` - Individual feature branches
- ``fix/issue-description`` - Bug fix branches

**Standard Workflow:**

1. **Create feature branch**:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make changes** following coding standards
3. **Run tests** and ensure all pass
4. **Run linting** and fix any issues
5. **Commit changes** with descriptive messages
6. **Push branch** and create pull request

Code Standards
--------------

**Formatting:**

We use automated code formatting tools:

.. code-block:: bash

   # Format code
   black .
   isort .

   # Check formatting (pre-commit will run these)
   black --check .
   isort --check-only .
   flake8 .

**Type Hints:**

- All functions must have type hints
- Use ``typing`` module for complex types
- Minimum 85% type coverage required

**Docstrings:**

Use Google-style docstrings:

.. code-block:: python

   def example_function(param1: str, param2: int) -> bool:
       """Brief description of the function.

       Longer description if needed explaining the function's behavior,
       use cases, or important details.

       Args:
           param1: Description of first parameter
           param2: Description of second parameter

       Returns:
           Description of return value

       Raises:
           ValueError: Description of when this exception is raised
           TypeError: Description of another exception
       """
       pass

**Error Handling:**

- Use specific exception types
- Provide meaningful error messages
- Log errors at appropriate levels
- Handle edge cases gracefully

Testing Guidelines
------------------

**Test Structure:**

.. code-block:: text

   tests/
   ├── test_cache.py              # Cache system tests
   ├── test_aws_integration.py    # AWS API mocking tests
   ├── test_configuration.py      # Configuration tests
   ├── test_output_formats.py     # Output generation tests
   ├── test_plugins.py            # Plugin system tests
   └── conftest.py                # Shared test fixtures

**Writing Tests:**

.. code-block:: python

   import pytest
   from moto import mock_ssm
   from aws_services_reporter.core.cache import AWSDataCache

   class TestCacheSystem:
       def test_cache_creation(self, tmp_path):
           """Test cache file creation and initialization."""
           cache_file = tmp_path / "test_cache.json"
           cache = AWSDataCache(str(cache_file))

           # Test implementation here
           assert cache is not None

**Running Tests:**

.. code-block:: bash

   # Run all tests with coverage
   python -m pytest tests/ -v --cov=aws_services_reporter --cov-report=term-missing

   # Run specific test file
   python -m pytest tests/test_cache.py -v

   # Run with debug output
   python -m pytest tests/test_cache.py -v -s

**Test Coverage:**

- Maintain minimum 80% overall coverage
- 95% coverage required for critical modules (cache, AWS client)
- Test both success and error scenarios
- Include edge cases and boundary conditions

Contribution Types
------------------

**Bug Fixes:**

1. **Create issue** describing the bug with reproduction steps
2. **Reference issue** in commit messages and PR
3. **Add regression test** to prevent future occurrences
4. **Update documentation** if behavior changes

**New Features:**

1. **Discuss feature** in GitHub issue before implementation
2. **Follow modular architecture** patterns
3. **Add comprehensive tests** for new functionality
4. **Update documentation** including user guides and API docs
5. **Consider backward compatibility** impact

**Plugin Development:**

1. **Follow plugin interface** defined in ``BaseOutputPlugin``
2. **Add to plugin directory** structure
3. **Include comprehensive tests** and examples
4. **Document plugin usage** and features
5. **Consider optional dependencies** and graceful fallbacks

**Documentation:**

1. **Use reStructuredText** format for Sphinx
2. **Include code examples** with proper syntax highlighting
3. **Test documentation** builds without errors
4. **Update relevant sections** consistently
5. **Follow existing documentation** style and structure

Code Review Process
-------------------

**Pull Request Guidelines:**

1. **Descriptive title** summarizing the change
2. **Detailed description** explaining what and why
3. **Link to related issues** using GitHub keywords
4. **Include screenshots** for UI/output changes
5. **Mark as draft** if work is in progress

**Review Criteria:**

- Code follows project standards and patterns
- Tests are comprehensive and pass
- Documentation is updated appropriately
- No breaking changes without justification
- Performance impact is considered

**Review Process:**

1. **Automated checks** must pass (CI/CD pipeline)
2. **Manual code review** by project maintainer
3. **Testing verification** in reviewer's environment
4. **Documentation review** for accuracy and completeness
5. **Final approval** and merge

Project Architecture
--------------------

Understanding the architecture helps with contributions:

**Module Structure:**

.. code-block:: text

   aws_services_reporter/
   ├── core/                  # Core functionality
   │   ├── config.py          # Configuration management
   │   ├── cache.py           # Intelligent caching
   │   └── progress.py        # UI and progress tracking
   ├── aws_client/            # AWS API integration
   │   ├── session.py         # AWS session management
   │   ├── ssm_client.py      # SSM Parameter Store client
   │   └── rss_client.py      # RSS feed integration
   ├── output/                # Output format generators
   │   ├── csv_output.py      # CSV format
   │   ├── json_output.py     # JSON format
   │   └── excel_output.py    # Excel format
   ├── plugins/               # Plugin system
   │   ├── base.py            # Abstract base class
   │   ├── discovery.py       # Plugin discovery
   │   └── xml_plugin.py      # XML plugin example
   └── utils/                 # Utilities
       ├── cli.py             # Command-line interface
       └── filters.py         # Filtering logic

**Design Principles:**

1. **Modularity**: Clear separation of concerns
2. **Extensibility**: Plugin architecture for new formats
3. **Performance**: Intelligent caching and concurrent processing
4. **Reliability**: Comprehensive error handling and testing
5. **Usability**: Rich CLI with progress tracking

Common Development Tasks
------------------------

**Adding a New Output Format:**

1. Create new file in ``aws_services_reporter/output/``
2. Implement format-specific generation function
3. Add format to CLI choices in ``utils/cli.py``
4. Update main.py format handling logic
5. Add comprehensive tests
6. Update documentation

**Adding CLI Options:**

1. Add to ``Config`` dataclass in ``core/config.py``
2. Add CLI argument in ``utils/cli.py``
3. Update ``create_config_from_args`` function
4. Add validation if needed
5. Update help text and documentation

**Modifying AWS Integration:**

1. Update relevant client in ``aws_client/`` directory
2. Consider caching implications for data changes
3. Add/update tests with moto mocking
4. Update error handling for new API calls
5. Document any new IAM permissions needed

Performance Considerations
--------------------------

**Optimization Guidelines:**

- Profile code with ``cProfile`` for performance hotspots
- Use concurrent processing for I/O-bound operations
- Implement streaming for large datasets
- Consider memory usage with large regions/services counts
- Optimize cache hit rates and invalidation logic

**Performance Testing:**

.. code-block:: bash

   # Profile application performance
   python -m cProfile -o profile_stats.prof main.py

   # Analyze profile results
   python -c "import pstats; pstats.Stats('profile_stats.prof').sort_stats('cumulative').print_stats(20)"

Release Process
---------------

**Version Management:**

- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in relevant files consistently
- Tag releases in Git with version numbers
- Update CHANGELOG.md with release notes

**Release Checklist:**

1. **Run full test suite** and ensure 100% pass rate
2. **Update documentation** including version references
3. **Run security scans** (bandit) and address issues
4. **Test installation** in clean environment
5. **Update ROADMAP.md** with completed features
6. **Create release** with comprehensive notes

Security Guidelines
-------------------

**Security Best Practices:**

1. **Never commit credentials** or sensitive data
2. **Use secure dependencies** (defusedxml, requests)
3. **Validate all user inputs** and file paths
4. **Handle errors** without exposing sensitive information
5. **Follow least privilege** principle for AWS permissions

**Security Testing:**

.. code-block:: bash

   # Run security analysis
   bandit -r aws_services_reporter/ -f json -o security_report.json

   # Check for known vulnerabilities
   safety check

Getting Help
------------

**Resources:**

- Project documentation (this site)
- GitHub Issues for bug reports and feature requests
- Code examples in tests and existing implementations
- AWS documentation for API references

**Communication:**

- **GitHub Issues** for bugs, features, and questions
- **Pull Request discussions** for code-specific questions
- **Documentation** for usage and architecture questions

**Best Practices for Getting Help:**

1. **Search existing issues** before creating new ones
2. **Provide minimal reproduction** examples for bugs
3. **Include relevant logs** and error messages
4. **Specify your environment** (Python version, OS, etc.)
5. **Be specific** about expected vs actual behavior

Thank You
---------

Thank you for contributing to AWS Services Reporter! Your contributions help make this tool better for everyone in the AWS community.

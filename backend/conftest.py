[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.development"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--strict-markers --tb=short -v"
testpaths = ["apps"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests"
]

[tool.coverage.run]
source = ["apps"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]

#!/bin/sh -e

# Clean up the build artifacts.
rm -rf build dist site *.egg-info *.egg .mypy_cache .pytest_cache .coverage .tox .ruff_cache

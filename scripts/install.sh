#!/bin/sh -e

pip install --upgrade pip
pip install --no-cache-dir -e '.[dev,test]'

pre-commit install
pre-commit autoupdate

if command -v pyenv 1>/dev/null 2>&1; then
    pyenv rehash
fi

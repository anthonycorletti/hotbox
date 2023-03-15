#!/bin/sh -ex

mypy hotbox tests
black hotbox tests --check
ruff hotbox tests scripts

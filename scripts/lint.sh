#!/bin/sh -ex

mypy pyrocloud tests
black pyrocloud tests --check
ruff pyrocloud tests scripts

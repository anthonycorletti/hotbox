#!/usr/bin/env bash

mkdocs build

cp ./docs/index.md ./README.md

git add ./docs README.md && git commit -S -m "doc: built and updated docs"

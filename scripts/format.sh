#!/bin/sh -ex

black hotbox tests scripts
ruff hotbox tests scripts --fix

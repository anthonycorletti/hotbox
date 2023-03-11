#!/bin/sh -ex

black pyrocloud tests scripts
ruff pyrocloud tests scripts --fix

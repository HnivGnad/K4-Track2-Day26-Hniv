#!/bin/sh
# Run the unchanged Makefile and kit with the local Linux toolchain.
set -eu
cd "$(dirname "$0")"
ROOT=$(pwd)
export RUNNER_PYTHON="$ROOT/.venv/linux-runtime/cpython-3.12.14-linux-x86_64-musl/bin/python3.12"
export PYTHONPATH="$ROOT/.venv/Lib/site-packages"
# Avoid the Windows-created pytest cache; this does not exclude tests.
export PYTEST_ADDOPTS="-p no:cacheprovider"
exec "$ROOT/.venv/linux-tools/bin/make" test BIN=.venv/linux-tools/bin

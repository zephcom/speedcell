#!/bin/sh
set -e
# Build MicroPython's Unix port and place the binary in ../bin
WORKDIR="$(pwd)"
BUILD_DIR="$WORKDIR/.micropython_build"

if [ ! -d "$BUILD_DIR" ]; then
  git clone https://github.com/micropython/micropython.git "$BUILD_DIR"
fi
cd "$BUILD_DIR"
make -C mpy-cross -j$(nproc)
cd ports/unix
make submodules
make -j$(nproc)
cp build-standard/micropython "$WORKDIR/bin/micropython"


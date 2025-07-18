# Speedcell MicroPython Environment

This repository includes a prebuilt MicroPython binary for quick testing.

## Usage

Run the included Unix MicroPython build:

```sh
./bin/micropython -c "print('hello from micropython')"
```

## Rebuilding

To rebuild the binary (for example after updating the source or changing
compiler flags), run:

```sh
scripts/build_micropython_unix.sh
```

The script clones the MicroPython repository into `.micropython_build` and
compiles the Unix port. The resulting binary is copied into `bin/micropython`.


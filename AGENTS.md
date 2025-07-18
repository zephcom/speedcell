# Repo Guidelines

- Use the precompiled MicroPython binary located at `bin/micropython` when running MicroPython scripts.
- If you need to rebuild or update this binary, execute `scripts/build_micropython_unix.sh`. This script clones the MicroPython repository into `.micropython_build` and compiles the Unix port.
- Keep the binary path (`bin/micropython`) intact so that any tools depending on it continue to work.
- No tests are present yet. When adding them, ensure they can run using the included binary.

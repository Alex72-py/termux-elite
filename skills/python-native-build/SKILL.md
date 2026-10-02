---
name: python-native-build
description: Diagnose a failed Python install on Termux or Android (compiler or header errors, Rust or maturin builds, no wheel for this platform, glibc wheels that fail at import, externally-managed-environment) and pick the smallest fix, preferring Termux-packaged libraries over source builds. Use when pip or uv fails, when a build error mentions clang, cc, cargo, rustc or a missing .h file, or when an import fails right after a successful install. Do NOT use for slow downloads, pure-Python packages that install fine, or Node problems (see node-native-build).
triggers: pip failed,python package install,wheel unavailable,build error,externally-managed-environment,failed building wheel,cargo failed,cannot locate symbol
risk: medium
---
# Python Native Build

## Purpose
Separate a Python packaging problem from a missing Termux toolchain, an unsupported Android wheel, or the wrong environment boundary, then apply the smallest change that fixes it.

## When to use
- `pip` or `uv` fails with compiler errors, missing headers, linker errors, Rust build errors, or `No matching distribution`.
- A package installs but fails on import.
- `error: externally-managed-environment`.

## When NOT to use
- Slow installs. Do not add a toolchain because a build is merely slow.
- Failures before pip runs (`pkg` errors): use `package-troubleshooting`.
- Node packages: use `node-native-build`.

## Preconditions
Capture, read-only: `python -VV`, `python -m pip --version`, `uname -m`, the active prefix, whether a venv is active, the exact package and version, and the first meaningful error (not the last line). `sh scripts/check-toolchain.sh` prints the toolchain facts.

## Decision tree
1. Confirm native Termux versus proot (`proot-boundaries`) and use that side's package manager.
2. `externally-managed-environment`: create a venv for project dependencies. Add `--system-site-packages` when Termux-packaged libraries (for example numpy) should stay visible. Do not default to `--break-system-packages`.
3. Check for a Termux package before building from source: `pkg search python-<name>`. Heavy libraries such as numpy, scipy, cryptography, pillow and lxml are often packaged. Prefer them; a source build of these is slow and fragile.
4. No compatible wheel and no sdist support: say so and offer a substitute or a proot environment. Do not loop on `--no-binary`.
5. Source build: name the missing executable (`clang`, `make`, `cmake`, `pkg-config`, `rustc`, `cargo`) and the missing header or library separately. Termux headers ship inside the main package (`openssl`, `libffi`, `libxml2`, `libjpeg-turbo`), not in `-dev` packages.
6. Rust or maturin based builds (for example pydantic-core, cryptography): need `rust` and `binutils`, and some require `ANDROID_API_LEVEL` set to the device API level (`getprop ro.build.version.sdk`). Check the project's build error before setting it.
7. Scientific stacks that fail linking math symbols may need `MATHLIB=m` in the environment. Verify against the actual error first.
8. Installs fine, import fails with `cannot locate symbol` or a missing `libc.so.6`: a glibc (manylinux) wheel landed on Bionic. Treat as step 4.
9. Build dies with `Killed` or signal 9: lower parallelism (`MAKEFLAGS=-j1`, `CMAKE_BUILD_PARALLEL_LEVEL=1`) and see `background-processes`.
10. Do not use `--no-build-isolation` until the build requirements are understood; it hides the real dependency boundary.

## Failure signatures
| Signature | Layer | Next step |
| --- | --- | --- |
| `clang: not found`, `command 'cc' failed` | no compiler | install `clang` after confirmation |
| `fatal error: 'x.h' file not found` | missing library | find the owning package with `pkg search`, install it |
| `unable to find library -lx` | missing or wrong library | same as above; check `$PREFIX/lib` |
| `can't find Rust compiler` or MSRV error | no or old Rust | install or upgrade `rust` |
| `No matching distribution found` | no wheel for platform | step 3 or 4 |
| `cannot locate symbol` at import | glibc wheel on Bionic | step 8 |

## Safety
Installing packages, creating venvs, and exporting build flags change the environment: state the exact change and confirm. Third-party package repositories (for example tur-repo) widen the trust boundary; ask before adding one.

## Verification
Re-run the original install, then `python -c "import <module>"` and `python -m pip check`. Report what remains unsupported on Android.

## Rollback
Record every package and venv created for this attempt. Remove only those, and never delete a user environment without explicit approval.

## Handoffs
- `termux-environment` when architecture, Python, or toolchain facts are missing.
- `package-troubleshooting` when `pkg` itself fails.
- `proot-boundaries` when the package needs glibc.
- `background-processes` when the build is killed.
- `node-native-build` when the failing package is a Node module.

## Report
Root cause in one line (layer plus first real error), the single change applied, the verification result, and any limit that remains.

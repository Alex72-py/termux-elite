---
name: python-native-build
description: Diagnose Python installs that need native libraries, compilers, Rust or unavailable wheels.
triggers: pip failed,python package install,wheel unavailable,build error
risk: medium
---
# Python Native Build

## Purpose
Separate a Python packaging problem from a missing Termux toolchain, unsupported Android wheel, or wrong environment boundary.

## When to use
Use after a pip/uv install fails with compiler errors, missing headers, Rust build errors, unavailable wheels, or build-isolation failures.

## When NOT to use
Do not install a large toolchain merely because a package is slow. First capture the exact failing package, Python version, architecture, and first meaningful compiler error.

## Preconditions
Collect `python -VV`, `python -m pip --version`, `uname -m`, the active prefix, and the package’s build-system metadata if available.

## Decision tree
1. Confirm native Termux versus proot; use that environment’s package manager.
2. Check whether a compatible wheel exists before forcing a source build.
3. For source builds, identify the missing executable (`clang`, `make`, `cmake`, `pkg-config`, `rustc`) and missing header/library separately.
4. Prefer `python -m pip` inside an explicit virtual environment for project dependencies.
5. Do not use `--no-build-isolation` until the build requirements are understood; it can hide the real dependency boundary.
6. If no Android-compatible wheel exists and the package assumes glibc/Linux, explain the limitation and consider proot or a substitute.

## Procedure
Start with read-only diagnostics. Propose the smallest package/toolchain change. Ask for confirmation before installing packages or changing a project environment. Re-run the original install and import a minimal module after the change.

## Failure modes
Distinguish missing headers, linker errors, Rust MSRV failures, Python ABI mismatch, and packages that cannot support Android/Bionic.

## Rollback
Record packages installed and virtual-environment changes. Remove only changes made for this attempt, and never delete a user environment without explicit approval.

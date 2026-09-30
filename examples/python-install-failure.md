# Example: Python install failure

Request: `pip install cryptography` fails while building on a phone.

A host agent should select `python-native-build` because the request mentions a Python install and a build failure. It should then:

1. Determine native Termux versus proot.
2. Capture Python version, pip location, architecture, and the first compiler error.
3. Check whether a compatible wheel exists before installing a compiler toolchain.
4. Explain and confirm any package/toolchain changes.
5. Re-run the install and import a minimal module.
6. Report what changed and what remains unsupported on Android.

The skill is a procedure, not a command to run blindly.

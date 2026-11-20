set shell := ["bash", "-euo", "pipefail", "-c"]

# Lists the commands.
default:
    @just --list

# Checks the command file and public profile without network or builds.
check:
    just --fmt --check
    python3 tools/check-profile.py

# Runs the full validation.
verify: check

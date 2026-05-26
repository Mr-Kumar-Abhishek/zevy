# Contributing to Zevy Messenger

Thank you for your interest in contributing to Zevy! This document outlines
how to set up your development environment and contribute effectively.

## Development Setup

### Prerequisites

- Python 3.10+
- Rust 1.70+ with Cargo
- Git

### Quick Start

```bash
# Clone
git clone <repo-url> zevy && cd zevy

# Virtual environment
python -m venv .venv
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate       # macOS/Linux

# Python dependencies
pip install -r requirements.txt

# Build the Rust crypto engine
cd crypto_rust
pip install maturin
maturin develop --release
cd ..

# Verify everything works
pytest
```

## Project Layout

| Directory      | Purpose                                        |
|----------------|------------------------------------------------|
| `crypto_rust/` | Rust native module (ZKP + FHE via PyO3)        |
| `network/`     | Async networking (TCP, Wi-Fi Direct, Bluetooth) |
| `ui/`          | Kivy screens and KV layout files               |
| `tests/`       | pytest test suite                              |
| `docs/`        | SRS, SDD, implementation plan                  |

## Running Tests

```bash
pytest                    # Full suite
pytest tests/test_crypto.py  # Crypto only
pytest -v                 # Verbose output
```

## Code Style

- Python: PEP 8 with docstrings on all public classes and functions.
- Rust: Standard `rustfmt` formatting.
- Kivy KV files: 4-space indentation.

## Branching Strategy

- `master` — Stable, tested code.
- Feature branches — Create a branch for each feature or fix.

## Commit Messages

Use clear, descriptive commit messages:

```
Phase N: Brief description of what was accomplished
```

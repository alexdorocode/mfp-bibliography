# Contributing

## Principles

- Keep raw data immutable.
- Preserve provenance in all derived outputs.
- Use reproducible scripts for transformations.
- Keep scientific label, evidence tier, and benchmark role separate.

## Development

```bash
pip install -e .[dev]
pytest
python scripts/validate_repository.py
```

## Pull request expectations

- No real-source downloads or scraping unless explicitly approved by policy.
- No manual edits to files under `data/raw/`.
- Include tests for logic changes.

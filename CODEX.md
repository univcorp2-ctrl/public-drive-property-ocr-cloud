# CODEX Notes

## Project goal

Build a working automation that reads a target Google Drive folder, extracts property document text, creates structured investment analysis, and publishes CSV / Excel / TXT / JSON outputs through GitHub Actions artifacts.

## Default target folder

`11cA-CrY7rjlQlzdXywpT3i7PLRrXxOgD`

## Main commands

```bash
pip install -r requirements.txt
ruff check .
pytest -q
python -m property_ocr_pipeline run --input-dir samples --output-dir outputs
```

## CI

Workflow: `.github/workflows/property-ocr.yml`

Artifact: `property-ocr-outputs`

## Secrets

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `TARGET_DRIVE_FOLDER_ID`

Do not commit real service account JSON or API keys.

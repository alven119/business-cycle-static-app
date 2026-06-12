# FRED Live Smoke Test

This project keeps live FRED checks out of the default pytest suite. Use this manual smoke test only when you want to verify that the local FRED API key, provider, and raw CSV cache work against the real API.

## 1. Create `.env`

Create a local `.env` file in the repository root:

```bash
FRED_API_KEY=your_fred_api_key_here
```

Do not commit `.env`. The provider reads `FRED_API_KEY` from the environment, and `scripts/fred_smoke_test.py` calls `load_dotenv()` so local `.env` works for manual runs.

## 2. Confirm `.env` Is Ignored

Run:

```bash
git check-ignore -v .env
```

Expected result: git prints the `.gitignore` rule that ignores `.env`.

`.env.example` is allowed to be committed, but it must contain only a placeholder value.

## 3. Run Dry-Run

Dry-run does not require a real FRED API key and does not download data:

```bash
env -u FRED_API_KEY python scripts/update_data.py --series-id UNRATE --dry-run
```

Expected result: the command prints whether the raw cache is present.

## 4. Run a Small Live Download

After `.env` is configured, run:

```bash
python scripts/fred_smoke_test.py
```

By default this checks only:

- `UNRATE`
- `ICSA`

The script downloads a small recent observation window and writes CSV files under `data/raw/fred/`.

To test a specific series:

```bash
python scripts/fred_smoke_test.py --series-id UNRATE
```

To refresh existing cache files:

```bash
python scripts/fred_smoke_test.py --force-refresh
```

## 5. Confirm Raw Data Is Ignored

Run:

```bash
git check-ignore -v data/raw/fred/UNRATE.csv
git status --short --ignored
```

Expected result: raw CSV files appear only as ignored files, not as files staged or ready to commit.

## Common Errors

`FRED_API_KEY is not set`

The `.env` file is missing, has a different variable name, or the command is being run outside the repository root. Confirm `.env` exists and contains `FRED_API_KEY=...`.

`Failed to download FRED series ...`

The network may be unavailable, the FRED API may be temporarily down, or the request timed out. Retry later or confirm network access.

`FRED API error ...`

The API key may be invalid, rate limited, or the series ID may be invalid. Confirm the key and try a known series such as `UNRATE`.

Raw data appears in `git status`

Confirm `.gitignore` includes `data/raw/`, then run `git check-ignore -v data/raw/fred/UNRATE.csv`. Do not commit raw cache files.


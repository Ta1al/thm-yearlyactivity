# THM Yearly Activity

Fetch and plot TryHackMe yearly activity for a user.

## Requirements

- Python 3.10+ recommended
- Internet access (calls TryHackMe public APIs)

Install dependencies:

```pwsh
python -m pip install -r requirements.txt
```

## Usage

You can pass a username with flags or provide a TryHackMe profile URL as a positional input.

### Single year (defaults to current year if omitted)

```pwsh
python app.py --username YOUR_NAME
```

```pwsh
python app.py --username YOUR_NAME --year 2025
```

### Username via profile URL

```pwsh
python app.py https://tryhackme.com/p/ta1al
```

### Multiple years

```pwsh
python app.py --username ta1al --years 2023,2024,2025
```

### Year range

```pwsh
python app.py https://tryhackme.com/p/ta1al --year-start 2021 --year-end 2024
```

## Notes

- If a year has no data, it is skipped automatically.
- When multiple years are requested, data is combined into a single timeline plot.

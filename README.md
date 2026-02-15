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
If no username is provided, the prompt accepts a username or profile URL (comma-separated for multiple users).

### Single year (defaults to current year if omitted)

```pwsh
python app.py --username YOUR_NAME
```

```pwsh
python app.py --username YOUR_NAME --year 2025
```

If no year flags are provided, you will be prompted and can enter:

- `year`
- `year,year,year`
- `year-year`

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

### Compare multiple users

```pwsh
python app.py --users ta1al,Wardet.Wahaj --years 2024,2025,2026
```

```pwsh
python app.py --users https://tryhackme.com/p/ta1al,https://tryhackme.com/p/Wardet.Wahaj --year-start 2022 --year-end 2025
```

## Notes

- If a year has no data, it is skipped automatically.
- When multiple years are requested, data is combined into a single timeline plot.
- When multiple users are requested, each user is plotted as a separate line on the same chart.

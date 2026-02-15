import argparse
import datetime as dt
import sys
from typing import Dict, List, Tuple

import requests


PROFILE_URL = "https://tryhackme.com/api/v2/public-profile"
YEARLY_URL = "https://tryhackme.com/api/v2/public-profile/yearly-activity"


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Plot TryHackMe yearly activity for a user."
	)
	parser.add_argument(
		"input",
		nargs="?",
		help="Optional username or profile URL (e.g., https://tryhackme.com/p/username)",
	)
	parser.add_argument("-u", "--username", help="TryHackMe username")
	parser.add_argument("-y", "--year", type=int, help="Year (e.g., 2025)")
	parser.add_argument(
		"--years",
		help="Comma-separated list of years (e.g., 2023,2024,2025)",
	)
	parser.add_argument("--year-start", type=int, help="Start year for range")
	parser.add_argument("--year-end", type=int, help="End year for range")
	return parser.parse_args()


def prompt_if_missing(value: str | int | None, label: str) -> str:
	if value is None or (isinstance(value, str) and not value.strip()):
		return input(f"Enter {label}: ").strip()
	return str(value).strip()


def resolve_year(value: str | int | None) -> int:
	if value is None or (isinstance(value, str) and not value.strip()):
		return dt.date.today().year
	return int(value)


def parse_years(args: argparse.Namespace) -> List[int]:
	years: List[int] = []
	if args.years:
		for item in str(args.years).split(","):
			item = item.strip()
			if not item:
				continue
			years.append(int(item))

	if args.year_start is not None or args.year_end is not None:
		start = args.year_start if args.year_start is not None else resolve_year(None)
		end = args.year_end if args.year_end is not None else resolve_year(None)
		if start > end:
			start, end = end, start
		years.extend(range(start, end + 1))

	if not years:
		years = [resolve_year(args.year)]

	unique_years = sorted(set(years))
	return unique_years


def resolve_username(username: str | None, raw_input: str | None) -> str:
	candidate = username or raw_input
	if candidate is None or not str(candidate).strip():
		candidate = prompt_if_missing(None, "username or profile URL")

	text = str(candidate).strip()
	if text.startswith("http://") or text.startswith("https://"):
		parts = text.rstrip("/").split("/")
		if "p" in parts:
			index = parts.index("p")
			if index + 1 < len(parts):
				return parts[index + 1]
		return parts[-1]

	return text


def fetch_user_id(username: str) -> str:
	response = requests.get(PROFILE_URL, params={"username": username}, timeout=30)
	response.raise_for_status()
	payload = response.json()
	user_id = payload.get("data", {}).get("_id")
	if not user_id:
		raise ValueError("User ID not found in response.")
	return user_id


def fetch_yearly_activity(user_id: str, year: int) -> List[Dict[str, object]] | None:
	response = requests.get(
		YEARLY_URL, params={"user": user_id, "year": year}, timeout=30
	)
	if response.status_code == 404:
		return None
	response.raise_for_status()
	payload = response.json()
	activity = payload.get("data", {}).get("yearlyActivity", [])
	if not isinstance(activity, list):
		raise ValueError("Yearly activity data not found in response.")
	return activity


def build_date_series(
	year: int, activity: List[Dict[str, object]]
) -> Tuple[List[dt.date], List[int]]:
	activity_map: Dict[dt.date, int] = {}
	for entry in activity:
		date_str = str(entry.get("date", ""))
		count = int(entry.get("count", 0) or 0)
		try:
			date_value = dt.date.fromisoformat(date_str)
		except ValueError:
			continue
		activity_map[date_value] = count

	start_date = dt.date(year, 1, 1)
	today = dt.date.today()
	end_of_year = dt.date(year, 12, 31)
	end_date = min(today, end_of_year)

	if start_date > end_date:
		raise ValueError("Year is in the future.")

	dates: List[dt.date] = []
	counts: List[int] = []
	cursor = start_date
	while cursor <= end_date:
		dates.append(cursor)
		counts.append(activity_map.get(cursor, 0))
		cursor += dt.timedelta(days=1)
	return dates, counts


def build_combined_series(
	years: List[int], activities_by_year: Dict[int, List[Dict[str, object]]]
) -> Tuple[List[dt.date], List[int]]:
	activity_map: Dict[dt.date, int] = {}
	for year in years:
		activity = activities_by_year.get(year, [])
		for entry in activity:
			date_str = str(entry.get("date", ""))
			count = int(entry.get("count", 0) or 0)
			try:
				date_value = dt.date.fromisoformat(date_str)
			except ValueError:
				continue
			activity_map[date_value] = activity_map.get(date_value, 0) + count

	if not years:
		raise ValueError("No years provided for combined series.")

	start_date = dt.date(min(years), 1, 1)
	today = dt.date.today()
	end_of_last_year = dt.date(max(years), 12, 31)
	end_date = min(today, end_of_last_year)

	if start_date > end_date:
		raise ValueError("Year range is in the future.")

	dates: List[dt.date] = []
	counts: List[int] = []
	cursor = start_date
	while cursor <= end_date:
		dates.append(cursor)
		counts.append(activity_map.get(cursor, 0))
		cursor += dt.timedelta(days=1)

	return dates, counts


def plot_activity(
	username: str, year_label: str, dates: List[dt.date], counts: List[int]
) -> None:
	import matplotlib.dates as mdates
	import matplotlib.pyplot as plt

	fig, axis = plt.subplots(figsize=(12, 4))
	axis.plot(dates, counts, color="#2c7fb8", linewidth=1.2)
	axis.fill_between(dates, counts, color="#7fcdbb", alpha=0.3)

	axis.set_title(f"TryHackMe Activity for {username} in {year_label}")
	axis.set_ylabel("Daily count")
	axis.set_xlabel("Date")

	axis.xaxis.set_major_locator(mdates.AutoDateLocator())
	axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(axis.xaxis.get_major_locator()))
	axis.grid(True, linestyle="--", alpha=0.4)

	fig.tight_layout()
	plt.show()


def main() -> int:
	args = parse_args()
	username = resolve_username(args.username, args.input)
	try:
		years = parse_years(args)
	except ValueError:
		print("Year values must be numbers.")
		return 1

	try:
		print(f"Fetching user ID for '{username}'...")
		user_id = fetch_user_id(username)
		print(f"User ID found: {user_id}")
		activities_by_year: Dict[int, List[Dict[str, object]]] = {}
		for year in years:
			print(f"Fetching yearly activity for {year}...")
			activity = fetch_yearly_activity(user_id, year)
			if activity is None:
				print(f"No data found for {year}; skipping.")
				continue
			print(f"Fetched {len(activity)} activity records.")
			activities_by_year[year] = activity
		if not activities_by_year:
			print("No yearly activity data found for any requested year.")
			return 0

		combined_years = sorted(activities_by_year.keys())
		dates, counts = build_combined_series(combined_years, activities_by_year)
		label = (
			str(combined_years[0])
			if len(combined_years) == 1
			else f"{combined_years[0]}-{combined_years[-1]}"
		)
		plot_activity(username, label, dates, counts)
	except requests.RequestException as exc:
		print(f"Request failed: {exc}")
		return 1
	except ValueError as exc:
		print(f"Error: {exc}")
		return 1

	return 0


if __name__ == "__main__":
	sys.exit(main())

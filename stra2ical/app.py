import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import requests
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from icalendar import Calendar, Event

app = FastAPI()


@app.get("/")
def status() -> str:
    return "Online."


@app.get("/calendar", response_class=PlainTextResponse)
async def calendar():
    await download(1)  # Download latest page of activities daily
    create_calendar()  # Create a new ics file
    with open("calendar/Strava.ics", encoding="UTF-8") as f:
        return f.read()  # Return ics file as string.


def assemble_dataframe() -> pl.DataFrame:
    return (
        pl.scan_parquet("activities/*.parquet")
        .with_columns(
            pl.col("start_date").str.strptime(pl.Datetime),
            (1e6 * pl.col("elapsed_time")).cast(pl.Duration).alias("elapsed"),
        )
        .with_columns((pl.col("start_date") + pl.col("elapsed")).alias("end_date"))
        .select("name", "start_date", "end_date", "distance")
        .unique()
        .sort("start_date", descending=True)
        .collect()
    )


def create_calendar() -> str:
    df = assemble_dataframe()
    logging.info("Collected dataframe.")
    cal = Calendar()
    cal.add("prodid", "-//Strava Activities//")
    cal.add("version", "2.0")

    successful_event_counter = 0
    for row in df.iter_rows(named=True):
        try:
            event = Event()
            summary = row["name"]
            if np.isfinite(row["distance"]) and row["distance"] > 0:
                summary += f""" ({np.round(row["distance"]/1000,1)}km)"""
            event.add("summary", summary)
            event.add("dtstart", row["start_date"])
            event.add("dtend", row["end_date"])
            cal.add_component(event)
            successful_event_counter += 1
        except Exception as exception:
            logging.error(exception)
    message = f"Created {successful_event_counter} events."
    logging.info(message)

    # Write to disk
    directory = Path.cwd() / "calendar"
    directory.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(directory, "Strava.ics"), "wb") as f:
        f.write(cal.to_ical())
    logging.info("Writing to Stava.ics completed.")
    return message


async def download(page: int) -> dict[str, int]:
    update_token()
    # Get the tokens from file to connect to Strava
    with open("stra2ical/.strava_tokens.json", encoding="UTF-8") as json_file:
        strava_tokens = json.load(json_file)
        access_token = strava_tokens["access_token"]

    url = f"https://www.strava.com/api/v3/athlete/activities?per_page=200&page={page}"
    r = requests.get(url + "&access_token=" + access_token, timeout=60)
    if r.status_code == 200:
        # Get the current datetime
        # Convert the datetime to a filename-friendly format with milliseconds
        now = datetime.now().strftime("%Y%m%dT%H%M%S%f")[
            :-3
        ]  # Keep only 3 decimal places for milliseconds

        pl.from_dicts(r.json(), infer_schema_length=None).write_parquet(
            f"activities/{now}.parquet"
        )
    return {"status": r.status_code}


async def download_all():
    for page in range(1, 200):
        try:
            await download(page)
        except Exception:
            break


def update_token():
    # Get the tokens from file to connect to Strava
    with open("stra2ical/.strava_tokens.json", encoding="UTF-8") as json_file:
        strava_tokens = json.load(json_file)
    with open("stra2ical/.app.json", encoding="UTF-8") as json_file:
        app_tokens = json.load(json_file)

    # If access_token has expired then
    # use the refresh_token to get the new access_token
    if strava_tokens["expires_at"] < time.time():
        # Make Strava auth API call with current refresh token
        response = requests.post(
            url="https://www.strava.com/oauth/token",
            data={
                "client_id": app_tokens["client_id"],
                "client_secret": app_tokens["client_secret"],
                "grant_type": "refresh_token",
                "refresh_token": strava_tokens["refresh_token"],
            },
            timeout=60,
        )
        # Save response as json in new variable
        new_strava_tokens = response.json()
        # Save new tokens to file
        with open("stra2ical/.strava_tokens.json", "w", encoding="UTF-8") as f:
            json.dump(new_strava_tokens, f)

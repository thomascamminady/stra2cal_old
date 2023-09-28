import os
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import requests
from icalendar import Calendar, Event

from stra2ical.authenticator import Authenticator
from stra2ical.utils.logger import logger


class DataManager:
    def __init__(
        self,
        location: str = "activities",
        calendar_root: str = "calendar",
        ics_filename: str = "Strava.ics",
    ):
        self.__location = location
        self.__calender_root = calendar_root
        self.__ics_filename = ics_filename
        directory = Path.cwd() / self.__calender_root
        directory.mkdir(parents=True, exist_ok=True)
        self.full_calendar_path = os.path.join(directory, self.__ics_filename)

    def assemble_data(self) -> pl.DataFrame:
        """Combine parquet files into dataframe."""
        return (
            pl.scan_parquet(f"{self.__location}/pages/*.parquet")
            .with_columns(
                pl.col("start_date").str.strptime(pl.Datetime),
                (1e6 * pl.col("elapsed_time")).cast(pl.Duration).alias("dt"),
            )
            .with_columns((pl.col("start_date") + pl.col("dt")).alias("end"))
            .select("name", "start_date", "end", "distance","id","start_latlng")
            .unique()
            .sort("start_date", descending=True)
            .collect()
        )

    def df_to_events(self, df: pl.DataFrame) -> list[Event]:
        """Turn dataframe into events."""
        events = []
        for row in df.iter_rows(named=True):
            try:
                event = Event()
                summary = row["name"]
                if np.isfinite(row["distance"]) and row["distance"] > 0:
                    summary += f""" ({np.round(row["distance"]/1000,1)}km)"""
                event.add("summary", summary)
                event.add("description",f"""https://www.strava.com/activities/{row["id"]}""")
                event.add("dtstart", row["start_date"])
                event.add("dtend", row["end"])
                events.append(event)
            except Exception as exception:
                logger.error(exception)
        return events

    def write_ics(self) -> None:
        """Write events to .ics."""
        df = self.assemble_data()
        cal = Calendar()
        cal.add("prodid", "-//Strava Activities//")
        cal.add("version", "2.0")

        events = self.df_to_events(df)
        for event in events:
            cal.add_component(event)

        message = f"Created {len(events)} events."
        logger.info(message)

        # Write to disk
        with open(self.full_calendar_path, "wb") as f:
            f.write(cal.to_ical())
        logger.info("Writing to Stava.ics completed.")

    async def download_activities_from_page(
        self, page: int, per_page: int = 200
    ) -> None:
        """Download recent activities."""
        auth = Authenticator()
        auth.update_token()
        # Get the tokens from file to connect to Strava
        access_token = str(auth.tokens_strava["access_token"])

        params = f"""per_page={per_page}&page={page}"""
        url = f"https://www.strava.com/api/v3/athlete/activities?{params}"
        result = requests.get(url + "&access_token=" + access_token, timeout=60)
        if result.status_code == 200:
            now = datetime.now().strftime("%Y%m%dT%H%M%S%f")[:-3]
            df = pl.from_dicts(result.json(), infer_schema_length=None)
            df.write_parquet(f"{self.__location}/pages/{now}.parquet")
            logger.info(f"Data that was downloaded has shape {df.shape}")

    async def download_all_activities(
        self, max_page: int = 200, per_page: int = 200
    ) -> None:
        """Download all activities."""
        for page in range(1, max_page):
            await self.download_activities_from_page(
                page=page,
                per_page=per_page,
            )

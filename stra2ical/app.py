from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from stra2ical.datamanager import DataManager

app = FastAPI()


@app.get("/")
def hello_world() -> str:
    """Print a "Hello, World!" message."""
    return "Hello, World!"


@app.get("/strava_calendar", response_class=PlainTextResponse)
async def strava_calendar() -> str:
    """Receive a calendar string."""
    # Set up a DataManager object.
    data_manager = DataManager()
    # Pull the latest 10 activities from Strava.
    # If this calendar is refreshed daily, this should be enough
    # unless you would hypothetically do more than 10 activities per day.
    await data_manager.download_activities_from_page(page=1, per_page=10)
    # Using the downloaded data, we create a .ics file on disk.
    data_manager.write_ics()
    # Return the content of the .ics file as a string so that you can subscribe
    # to this calendar.
    with open(data_manager.full_calendar_path, encoding="UTF-8") as f:
        return f.read()  # Return ics file as string.

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from stra2cal.datamanager import DataManager
from stra2cal.utils.logger import logger

app = FastAPI()


@app.get("/")
def hello_world() -> str:
    """Print a "Hello, World!" message."""
    logger.info("[ROUTE] /")
    return "Hello, World!"


@app.get("/strava_calendar", response_class=PlainTextResponse)
async def strava_calendar() -> str:
    """Receive a calendar string."""
    logger.info("[ROUTE] /strava_calendar")
    # Set up a DataManager object.
    data_manager = DataManager()
    # Pull the latest 5 activities from Strava.
    # If this calendar is refreshed daily, this should be enough
    # unless you would hypothetically do more than 5 activities per day.
    await data_manager.download_activities_from_page(page=1, per_page=5)
    # Using the downloaded data, we create a .ics file on disk.
    data_manager.write_ics()
    # Return the content of the .ics file as a string so that you can subscribe
    # to this calendar.
    with open(data_manager.full_calendar_path, encoding="UTF-8") as f:
        return f.read()  # Return ics file as string.


@app.get("/download_all")
async def download_all() -> None:
    """Downloads the last 200 pages that contain activities from Strava."""
    logger.info("[ROUTE] /download_all")
    await DataManager().download_all_activities()

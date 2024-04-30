# stra2cal

Add all your Strava activities to your calendar.

<img src="https://raw.githubusercontent.com/thomascamminady/stra2cal/main/Calendar_Week.png" width="45%" alt="Calendar Week"><img src="https://raw.githubusercontent.com/thomascamminady/stra2cal/main/Calendar_Month.png" width="45%" alt="Calendar Month">

## Authenticate

You have to first execute the steps presented in this [amazing tutorial by Benji Knights Johnson.](https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86)

You need to have two files inside the `stra2cal` folder:

`.client.json`

```json
{
  "client_id": 12345,
  "client_secret": "abc123abc123abc123abc123abc123abc123abc123"
}
```

And there should be a second file `.strava_tokens.json`. This is generated if you run the `authenticate.ipynb` that lives inside `notebooks/`. This is the script from Benji Knits Johnson's tutorial. The content of `.strava_tokens.json` looks like this:

```json
{
  "token_type": "Bearer",
  "access_token": "56756756756asdasdasdas56756756756asdasdasdas",
  "expires_at": 1711382710,
  "expires_in": 21600,
  "refresh_token": "xyz789xyz789xyz789xyz789xyz789"
}
```

## How to use?

Clone this repository and run `poetry install`.

The idea is that we are using `uvicorn` to host a webserver on your local machine and then we will subscribe to the hosted calendar.

The `start_app.sh` script is just starting the server. **_In the `start_app.sh` script, you have to update the path to the repository._**

```bash
nohup ./start_app.sh > nohup.log 2>&1 &
```

We can also add this as a `cronjob`, i.e., every six hours, we check if our server is still running and if not, we restart it. Run

````

We can also add this as a `cronjob`, i.e., every six hours, we check if our server is still running and if not, we restart it.

```bash
crontab -e
````

Add this entry

```bash
0 */6 * * * /path/to/the/script/stra2cal/start_app.sh
0 */6 * * * /Users/thomascamminady/Repos/stra2cal/start_app.sh
```

Next we have to **only once** manually trigger the download of all past Strava activities by opening a browser and visiting

```bash
127.0.0.1:7777/download_all
```

You only need to do this once to download all past activities. The subscription to the calendar will get the new daily workouts.

Then open `Calendar.app` and go to `File > New Calendar Subscription` and add

```bash
127.0.0.1:7777/strava_calendar
```

http://127.0.0.1:7777/strava_calendar

```

Set it to refresh daily. This will trigger a daily download of the last activities and will return the calendar entries.

## Documentation

Find this repository on [Github](https://github.com/thomascamminady/stra2cal) or check out the [documentation](https://thomascamminady.github.io/stra2cal).
```

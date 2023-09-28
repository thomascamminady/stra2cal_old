# stra2ical

Add all your Strava activities to your calendar.

![plot](https://raw.githubusercontent.com/thomascamminady/stra2ical/main/Calendar_Week.png)

![plot](https://raw.githubusercontent.com/thomascamminady/stra2ical/main/Calendar_Month.png)


## Authenticate

You have to first execute the steps presented in this [amazing tutorial by Benji Knights Johnson.](https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86)

## How to use?

The idea is that we are using `uvicorn` to host a webserver on your local machine and then we will subscribe to the hosted calendar.

The `start_app.sh` script is just starting the server.

```bash
nohup ./start_app.sh > nohup.log 2>&1 &
 ```
We can also add this as a `cronjob`, i.e., every six hours, we check if our server is still running and if not, we restart it.

```bash
crontab -e
0 */6 * * * /path/to/the/script/stra2ical/start_app.sh
```

Next we have to **only once** manually trigger the download of all past Strava activities by opening a browser and visiting

```
127.0.0.1:7777/download_all
```

You only need to do this once to download all past activities. The subscription to the calendar will get the new daily workouts.

Then open `Calendar.app` and go to `File > New Calendar Subscription` and add

```
127.0.0.1:7777/strava_calendar
```

Set it to refresh daily. This will trigger a daily download of the last activities and will return the calendar entries.





## Documentation
Find this repository on [Github](https://github.com/thomascamminady/stra2ical) or check out the [documentation](https://thomascamminady.github.io/stra2ical).

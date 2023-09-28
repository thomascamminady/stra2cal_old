import json
import time

import requests


class Authenticator:
    def __init__(
        self,
        path_json_strava: str = "stra2ical/.strava_tokens.json",
        path_json_client: str = "stra2ical/.client.json",
        encoding: str = "UTF-8",
    ):
        self.__path_json_strava = path_json_strava
        self.__path_json_client = path_json_client
        self.__encoding = encoding

    def __tokens(self, file) -> dict[str, str]:
        with open(file, encoding=self.__encoding) as json_file:
            tokens = json.load(json_file)
            return tokens

    @property
    def tokens_strava(self) -> dict[str, str]:
        """Get the Strava tokens as dict."""
        return self.__tokens(self.__path_json_strava)

    @property
    def tokens_client(self) -> dict[str, str]:
        """Get the client tokes as dict."""
        return self.__tokens(self.__path_json_client)

    def update_token(self):
        """Update token using refresh token."""
        # If access_token has expired then
        # use the refresh_token to get the new access_token
        if int(self.tokens_strava["expires_at"]) < time.time():
            # Make Strava auth API call with current refresh token
            response = requests.post(
                url="https://www.strava.com/oauth/token",
                data={
                    "client_id": self.tokens_client["client_id"],
                    "client_secret": self.tokens_client["client_secret"],
                    "grant_type": "refresh_token",
                    "refresh_token": self.tokens_strava["refresh_token"],
                },
                timeout=60,
            )
            # Save response as json in new variable
            new_strava_tokens = response.json()
            # Save new tokens to file
            with open(self.__path_json_strava, "w", encoding="UTF-8") as f:
                json.dump(new_strava_tokens, f)

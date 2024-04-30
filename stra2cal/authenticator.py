import json
import time

import requests


class Authenticator:
    def __init__(
        self,
        path_json_strava: str = "stra2cal/.strava_tokens.json",
        path_json_client: str = "stra2cal/.client.json",
        encoding: str = "UTF-8",
    ):
        self.__path_json_strava = path_json_strava
        self.__path_json_client = path_json_client
        self.__encoding = encoding

    def __tokens(self, file) -> dict[str, str]:
        try:
            with open(file, encoding=self.__encoding) as json_file:
                tokens = json.load(json_file)
                return tokens
        except FileNotFoundError:
            print(f"File {file} not found.")
            return {}

    @property
    def tokens_strava(self) -> dict[str, str]:
        """Get the Strava tokens as dict."""
        return self.__tokens(self.__path_json_strava)

    @property
    def tokens_client(self) -> dict[str, str]:
        """Get the client tokens as dict."""
        return self.__tokens(self.__path_json_client)

    def update_token(self):
        """Update token using refresh token."""
        if self._is_token_expired():
            self._refresh_token()

    def _is_token_expired(self) -> bool:
        """Check if the token has expired."""
        return int(self.tokens_strava.get("expires_at", 0)) < time.time()

    def _refresh_token(self):
        """Refresh the token."""
        response = requests.post(
            url="https://www.strava.com/oauth/token",
            data={
                "client_id": self.tokens_client.get("client_id"),
                "client_secret": self.tokens_client.get("client_secret"),
                "grant_type": "refresh_token",
                "refresh_token": self.tokens_strava.get("refresh_token"),
            },
            timeout=60,
        )
        if response.status_code == 200:
            self._save_new_tokens(response.json())
        else:
            print(f"Failed to refresh token. Status code: {response.status_code}")

    def _save_new_tokens(self, new_tokens: dict):
        """Save new tokens to file."""
        with open(self.__path_json_strava, "w", encoding=self.__encoding) as f:
            json.dump(new_tokens, f)

import os
import requests


class ApiClient:
    def __init__(self):
        self.base_url = os.getenv("MEMECAM_API_URL", "http://127.0.0.1:8000")
        self.token = None

    def set_token(self, token: str):
        self.token = token

    def build_url(self, path: str):
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def get_headers(self):
        headers = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def login(self, login: str, password: str):
        response = requests.post(
            self.build_url("/login"),
            json={
                "login": login,
                "password": password
            },
            headers=self.get_headers(),
            timeout=5
        )

        response.raise_for_status()
        data = response.json()

        self.token = data["access_token"]
        return data

    def get_me(self):
        response = requests.get(
            self.build_url("/me"),
            headers=self.get_headers(),
            timeout=5
        )

        response.raise_for_status()
        return response.json()

    def recognize_meme(self, meme_name: str, confidence: float):
        response = requests.post(
            self.build_url("/recognition"),
            json={
                "meme_name": meme_name,
                "confidence": confidence
            },
            headers=self.get_headers(),
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    def get_my_history(self):
        response = requests.get(
            self.build_url("/me/memes/history"),
            headers=self.get_headers(),
            timeout=5
        )

        response.raise_for_status()
        return response.json()
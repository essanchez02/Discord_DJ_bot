from flask import Flask, redirect, request, jsonify
import os
import requests
from urllib.parse import urlencode

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")

SCOPES = "user-read-private user-read-email user-read-recently-played user-top-read user-read-currently-playing"

@app.route("/")
def login():
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    })
    return redirect(auth_url)

@app.route("/link")
def link():
    discord_id = request.args.get("discord_id")

    if not discord_id:
        return "Missing Discord ID", 400

    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": discord_id  # <-- used later to link Spotify to Discord
    })

    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    discord_id = request.args.get("state")

    if not code:
        return "No code provided", 400
    if not discord_id:
        return "Missing Discord ID", 400

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    res = requests.post(token_url, data=payload)
    if res.status_code != 200:
        return f"Failed to get token: {res.text}", 400

    tokens = res.json()

    # Save tokens to JSON file
    import json
    if os.path.exists("tokens.json"):
        with open("tokens.json", "r") as f:
            token_db = json.load(f)
    else:
        token_db = {}

    token_db[discord_id] = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_in": tokens["expires_in"]
    }

    with open("tokens.json", "w") as f:
        json.dump(token_db, f, indent=2)

    return "Spotify account linked successfully! You can now use the bot."


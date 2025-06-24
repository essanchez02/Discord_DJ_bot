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

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

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
    return jsonify(tokens)

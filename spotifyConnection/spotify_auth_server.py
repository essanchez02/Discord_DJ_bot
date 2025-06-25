import os
import json
import requests
from urllib.parse import urlencode
from flask import Flask, redirect, request, jsonify

# ============================== Define Constants ==============================
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
SCOPES = "user-read-private user-read-email user-read-recently-played user-top-read user-read-currently-playing"

# ====================== Flask App Setup ======================
app = Flask(__name__)
@app.route("/")
def home():
    return "✅ Spotify OAuth server is running!"

# =========================== Spotify OAuth Endpoint ===========================
# This endpoint initiates the Spotify OAuth flow
@app.route("/link")
def link():
    # Get the Discord ID from the query parameters
    discord_id = request.args.get("discord_id")
    if not discord_id:
        return "Missing Discord ID", 400

    # Generate the Spotify authorization URL
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": discord_id  # <-- used later to link Spotify to Discord profile
    })

    # Redirect the user to the Spotify authorization page
    return redirect(auth_url)

# ============================= Callback Endpoint =============================
# This endpoint is called by Spotify after the user authorizes the app
@app.route("/callback")
def callback():
    # Get the authorization code and Discord ID from the query parameters
    code = request.args.get("code")
    discord_id = request.args.get("state")
    if not code:
        return "No code provided", 400
    if not discord_id:
        return "Missing Discord ID", 400

    # Exchange the authorization code for an access token
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

    # Save the tokens for this Discord user to a file on the railway volume
    # Note: This is a bandade solution. Later we will use a database.
    VOLUME_PATH = "/testVolume/tokens.json"
    if os.path.exists(VOLUME_PATH):
        with open(VOLUME_PATH, "r") as f:
            token_db = json.load(f)
    else:
        token_db = {}

    token_db[discord_id] = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_in": tokens["expires_in"]
    }

    with open(VOLUME_PATH, "w") as f:
        json.dump(token_db, f, indent=2)

    return "Spotify account linked successfully! You can now use the bot."

# =========================== Get Token Endpoint ===========================
# This endpoint retrieves the access token for a given Discord user
# It is used by the bot to make requests to the Spotify API
@app.route("/get_token/<discord_id>")
def get_token(discord_id):
    import json
    VOLUME_PATH = "/testVolume/tokens.json"

    if not os.path.exists(VOLUME_PATH):
        return jsonify({"error": "no token file"}), 404

    with open(VOLUME_PATH, "r") as f:
        token_db = json.load(f)

    if discord_id not in token_db:
        return jsonify({"error": "no token for this user"}), 404

    return jsonify(token_db[discord_id])

######## FOR DEBUGGING ONLY: View stored tokens ########
# @app.route("/tokens")
# def view_tokens():
#     import json
#     if not os.path.exists("tokens.json"):
#         return "No tokens found", 404
#     with open("tokens.json", "r") as f:
#         return jsonify(json.load(f))

# =========================== Run the Flask App ===========================
# This will run the Flask app on the specified port
# Make sure the PORT environment variable in Railway is set
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

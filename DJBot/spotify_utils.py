import os
import json
import requests
from profile_utils import load_profiles, save_profiles
# ====================== Constants ======================
VOLUME_DIR = "/testVolume"
TOKENS_FILE = os.path.join(VOLUME_DIR, "tokens.json")
PROFILE_FILE = "musicProfiles/profiles.json"

# ====================== Spotify API Utils ======================
# Check if the website has a token for the user
# This is a placeholder function until we use a real database
def get_remote_token(discord_id):
    url = f"https://discorddjbot-production.up.railway.app/get_token/{discord_id}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    return res.json()

def get_top_tracks(access_token, limit=10):
    # Fetch top tracks from Spotify API
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "limit": limit,
        "time_range": "medium_term"
    }
    url = "https://api.spotify.com/v1/me/top/tracks"

    # Make the request to Spotify API
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print(f"Spotify API error: {res.status_code} - {res.text}")
        return []
    data = res.json()

    # Extract relevant track information
    return [{
        "name": track["name"],
        "artist": track["artists"][0]["name"],
    } for track in data["items"]]


def update_user_profile(discord_id):
    # Fetch the access token from the remote API
    token_data = get_remote_token(discord_id)
    if not token_data:
        print("No token found for this user (via remote API).")
        return
    access_token = token_data["access_token"]

    # Fetch top tracks
    top_tracks = get_top_tracks(access_token)

    # Save top tracks under user's Discord ID
    profiles = load_profiles()
    profiles[str(discord_id)] = {
        "top_tracks": top_tracks
    }
    save_profiles(profiles)

    print(f"✅ Updated profile for {discord_id}")
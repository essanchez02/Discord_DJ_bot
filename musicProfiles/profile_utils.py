import json
import requests
import os
from datetime import datetime

PROFILE_PATH = "musicProfiles/profiles.json"

def load_profiles():
    if not os.path.exists(PROFILE_PATH):
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        with open(PROFILE_PATH, "w") as f:
            json.dump({}, f)
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILE_PATH, "w") as f:
        json.dump(profiles, f, indent=4)

def get_or_create_profile(user):
    profiles = load_profiles()
    user_key = f"{user.name}#{user.discriminator}"

    if user_key not in profiles:
        profiles[user_key] = {
            "songs_played": 0,
            "favorite_genres": [],
            "liked_songs": [],
            "recent_artists": [],
            "joined": datetime.now().isoformat(),
        }
        save_profiles(profiles)
    
    return profiles[user_key]

def get_top_tracks(access_token, limit=10):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "limit": limit,
        "time_range": "medium_term"
    }
    url = "https://api.spotify.com/v1/me/top/tracks"

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print(f"Spotify API error: {res.status_code} - {res.text}")
        return []

    data = res.json()
    return [{
        "name": track["name"],
        "artist": track["artists"][0]["name"],
        "uri": track["uri"]
    } for track in data["items"]]


def update_user_profile(discord_id):
    # Load tokens
    with open("tokens.json", "r") as f:
        token_db = json.load(f)

    token_data = token_db.get(str(discord_id))
    if not token_data:
        print("No token found for this user.")
        return

    access_token = token_data["access_token"]

    # Fetch top tracks
    top_tracks = get_top_tracks(access_token)

    # Load or create profile.json
    if os.path.exists("profile.json"):
        with open("profile.json", "r") as f:
            profiles = json.load(f)
    else:
        profiles = {}

    # Save top tracks under user's Discord ID
    profiles[str(discord_id)] = {
        "top_tracks": top_tracks
    }

    with open("profile.json", "w") as f:
        json.dump(profiles, f, indent=2)

    print(f"Updated profile for {discord_id}")


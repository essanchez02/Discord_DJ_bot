import json
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

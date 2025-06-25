import os
import json
from datetime import datetime

# ============================== Define Constants ==============================
PROFILE_PATH = "musicProfiles/profiles.json"

# ====================== Profile Management Functions ======================
def load_profiles():
    # Create the directory if it doesn't exist
    if not os.path.exists(PROFILE_PATH):
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        # Create an empty profile file if it doesn't exist
        with open(PROFILE_PATH, "w") as f:
            json.dump({}, f)

    # Load the profiles from the JSON file
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def save_profiles(profiles):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    # Save the profiles to the JSON file
    with open(PROFILE_PATH, "w") as f:
        json.dump(profiles, f, indent=4)

def get_or_create_profile(member):
    # Load existing profiles
    profiles = load_profiles()
    # Get the user ID
    user_id = str(member.id)
    # If the user does not already have a profile, create one
    if user_id not in profiles:
        profiles[user_id] = {
            "rated songs": [
                {
                    "name": "fake name",
                    "artist": "fake artist",
                    "rating": 3,
                    "last played": datetime.now().isoformat(),
                    "tags": []
                }],
            "joined": datetime.now().isoformat(),
        }
        save_profiles(profiles)
    
    return profiles[user_id]


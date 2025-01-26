import datetime
import os
import json
import tweepy
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load API keys
load_dotenv(override=True)

# YouTube API setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Twitter API setup
client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"), 
    consumer_secret=os.getenv("TWITTER_API_SECRET_KEY"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
)

def get_channel_stats(channel_id):
    """Fetch stats for a YouTube channel."""
    request = youtube.channels().list(
        part="statistics,snippet",
        id=channel_id
    )
    response = request.execute()
    return response

CHANNELS_FILE = 'channels.json'

def load_channels():
    """Load channels from JSON file."""
    with open(CHANNELS_FILE, 'r') as f:
        return json.load(f)

def save_channels(channels):
    """Save channels to JSON file."""
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f, indent=4)

def load_json(filename):
    """Load JSON from a file. Return an empty dictionary if the file is empty or invalid."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {filename} is empty or contains invalid JSON. Initializing as empty.")
            return {}  # Return an empty dictionary if JSON is invalid
    else:
        return {}  # Return an empty dictionary if the file doesn't exist


def save_json(data, filename):
    """Generic function to save JSON to a file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

MILESTONES_FILE = 'milestone_history.json'

def add_milestone_to_history(channel_id, channel_username, milestone):
    """Add milestone to channel history, ensuring consistency with channel ID and username."""
    milestones = load_json(MILESTONES_FILE)
    
    # Check if the channel ID exists in the JSON data
    if channel_id in milestones:
        # Verify if the channel username matches
        if milestones[channel_id]['username'] != channel_username:
            # Update the channel username if it has changed
            print(f"Username for channel {channel_id} has changed from {milestones[channel_id]['username']} to {channel_username}. Updating...")
            milestones[channel_id]['username'] = channel_username
        
        # Append the new milestone
        milestones[channel_id]['history'].append({
            'milestone': milestone,
            'date': datetime.datetime.now().strftime('%Y-%m-%d')  # Correct datetime usage
        })
    else:
        # New channel entry
        milestones[channel_id] = {
            'username': channel_username,
            'history': [{
                'milestone': milestone,
                'date': datetime.datetime.now().strftime('%Y-%m-%d')
            }]
        }
        print(f"Added new channel {channel_id} with username {channel_username}.")

    # Save back to the milestones file
    save_json(milestones, MILESTONES_FILE)
    print(f"Milestone {milestone} added for channel {channel_username} ({channel_id}).")

def tweet_milestones(channel_name, channel_username, milestones):
    """Post a tweet about a milestone."""
    milestones_str = ', '.join(f'{m/1000000}M' for m in milestones)
    channel_name_cleaned = channel_name.replace(" ", "")
    channel_username_cleaned = channel_username.lstrip("@")

    if channel_name_cleaned.lower() != channel_username_cleaned.lower():
        tweet = f"{channel_name} passed {milestones_str} subscribers on YouTube! #{channel_username_cleaned} #{channel_name_cleaned} #YouTube"
    else:
        tweet = f"{channel_name} passed {milestones_str} subscribers on YouTube! #{channel_username_cleaned} #YouTube"

    # tweet = f"{channel_name} passed {milestones_str} subscribers on YouTube! #{channel_username_cleaned} #{channel_name_cleaned} #YouTube"
    
    response = client.create_tweet(text=tweet)
    print(response)
    print(f"Tweeted milestones for {channel_name}: {milestones_str}")

def check_and_update_milestones():
    """Check channels and update milestones in JSON file."""
    # Load current channels
    channels = load_channels()
    
    # Iterate through each channel
    for channel_id, channel_data in channels.items():
        # Get current channel stats
        data = get_channel_stats(channel_id)
        channel_name = data["items"][0]["snippet"]["title"]
        channel_username = data["items"][0]["snippet"]["customUrl"] 
        current_subs = int(data["items"][0]["statistics"]["subscriberCount"])
        current_target = channel_data['target']

        # Track milestones crossed
        milestones_crossed = []
        
         # Check milestones progressively
        while current_subs >= current_target:
            milestones_crossed.append(current_target)

            # Add milestone to history
            add_milestone_to_history(channel_id, channel_username, current_target)

            current_target = ((current_target // 1000000) + 1) * 1000000
        
        # Tweet all crossed milestones in one tweet if any
        if milestones_crossed:
            tweet_milestones(channel_name, channel_username, milestones_crossed)
            
            # Update JSON with new target
            channels[channel_id]['target'] = current_target
            save_channels(channels)
            print(f"Updated {channel_name} milestone. New target: {current_target}")
        else:
            print(f"{channel_name} is at {current_subs} subscribers. Target: {current_target}")

if __name__ == "__main__":
    # Run milestone check and update
    check_and_update_milestones()
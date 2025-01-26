import os
import json
import time
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

# Load API keys
load_dotenv(override=True)

print(os.getenv("YOUTUBE_API_KEY"))

# YouTube API setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Function to build the YouTube API client
def build_youtube_client():
    return googleapiclient.discovery.build(
        'youtube', 'v3', developerKey=YOUTUBE_API_KEY )

# Function to search the YouTube channel by name and get details
def search_channel_by_name(youtube, channel_name):
    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    response = request.execute()

    if response['items']:
        channel_id = response['items'][0]['snippet']['channelId']
        channel_title = response['items'][0]['snippet']['channelTitle']
        return channel_id, channel_title
    return None, None

# Function to get the current subscriber count of a channel by ID
def get_channel_details(youtube, channel_id):
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    
    if response['items']:
        curr_subs = int(response['items'][0]['statistics']['subscriberCount'])
        return curr_subs
    return None

# Function to load channel names from a text file
def load_channel_names(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]
    
# Save the updated channels to channels.json
# def save_channels_to_json(popular_channels, file_path):
#     with open(file_path, 'w', encoding='utf-8') as json_file:
#         json.dump(popular_channels, json_file, indent=4)

def save_channels_to_json(popular_channels, file_path):
    # Load existing data if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = {}

    # Merge new data with existing data
    existing_data.update(popular_channels)

    # Write the combined data back to the file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4)

def load_existing_channels(file_path):
    if os.path.exists(file_path):
        # Check if the file is empty
        if os.path.getsize(file_path) == 0:
            return {}  # Return an empty dictionary if the file is empty
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)  # Load existing JSON data
    return {}  # Return an empty dictionary if the file doesn't exist


# Function to periodically save data after a certain number of channels
def periodically_save(popular_channels, file_path, save_threshold=10):
    # If the number of entries exceeds the threshold, save periodically
    if len(popular_channels) % save_threshold == 0:
        print(f"Saving data after {len(popular_channels)} channels processed...")
        save_channels_to_json(popular_channels, file_path)
        time.sleep(1)  # Adding sleep to avoid excessive file writes (optional)

# Main function to process the channels
def main():
    youtube = build_youtube_client()
    
    channel_names = load_channel_names('channelname.txt')  # Replace with your file path
    popular_channels = load_existing_channels('channels.json')

    for channel_name in channel_names:
        print(f"Processing channel: {channel_name}")

        # Skip channels already in the JSON file
        if any(channel_name in channel['name'] for channel in popular_channels.values()):
            print(f"Skipping {channel_name}, already processed.")
            continue
        
        # Search for the channel by name
        channel_id, channel_title = search_channel_by_name(youtube, channel_name)
        
        if channel_id:
            # Get subscriber count
            curr_subs = get_channel_details(youtube, channel_id)
            
            if curr_subs and curr_subs >= 10000000:
                # Store channel information if subs >= 10 million

                target = ((curr_subs // 1000000) + 1) * 1000000 

                popular_channels[channel_id] = {
                    'name': channel_title,
                    'target': target
                }
                print(f"Added {channel_title} with current subscribers : {curr_subs} and target subscribers : {target}.")

                # Periodically save the data to avoid losing progress if interrupted
                periodically_save(popular_channels, 'channels.json')
            else:
                popular_channels["not found"] = {
                'name': channel_name,
                'target': 0
                }
                print(f"Channel {channel_name} not found.")

                # Periodically save the data
                periodically_save(popular_channels, 'channels.json')
        else :
            popular_channels["not found"] = {
                'name': channel_name,
                'target': 0
            }
            print(f"Channel {channel_name} not found.")
    
    # After processing all channels, save the final data to channels.json
    save_channels_to_json(popular_channels, 'channels.json')
    
    print(f"Finished processing. Popular channels saved to channels.json.")

if __name__ == '__main__':
    main()

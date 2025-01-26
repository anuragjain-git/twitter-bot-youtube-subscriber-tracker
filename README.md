# YouTube Subscriber Tracker Twitter Bot

This Twitter bot that monitors the top 500 most subscribed YouTube channels subscriber count and posts a tweet whenever a channel reaches a 1 million subscriber increase. The bot uses the **YouTube Data API** to fetch subscriber counts and the **Twitter API** to post tweets.

##  Demo
You can check out the bot on Twitter: [YoutubeStatsBot](https://x.com/YoutubeStatsBot)

## Medium Blog

Learn how to build this Twitter bot. Step-by-step guide with API integration and deployment tips.
For a detailed tutorial on how to build this bot, check out the [full guide on Medium](https://medium.com/@anurag-jain/how-to-create-a-twitter-bot-using-python-d350a720359b).

## How to Install

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/twitter-bot-youtube-subscriber-tracker.git

2. Install the required dependencies by using the requirements.txt file:
   ```bash
   pip install -r requirements.txt

3. Set up your **API keys**:
   - Follow the instructions in the [Twitter Developer Documentation](https://developer.twitter.com/en/docs) to obtain your Twitter API keys.
   - Follow the instructions in the [YouTube Data API Guide](https://developers.google.com/youtube/v3) to obtain your YouTube API key.

4. Create a .env file in the root of the project and add your API keys:
   ```bash
   YOUTUBE_API_KEY=your_youtube_api_key
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET_KEY=your_twitter_secret_key
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_token_secret

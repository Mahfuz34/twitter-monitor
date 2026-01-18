import asyncio
import json
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright
import aiohttp
import logging

# Configuration
TWITTER_USERNAME = "Gold_Cryptoz"
TWITTER_URL = f"https://x.com/{TWITTER_USERNAME}"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1462469762625044705/raA1mxIotEeoDwEYgOD-64m5nwf19SKitqMneaaYiz8hprm8mh44-yq8ufYq2lyUWGQq"
PUSHOVER_USER_KEY = "ubmu2gu7mey1xvir5yym731p92mj8n"
PUSHOVER_API_TOKEN = "ag57t6qmvv45wf1fx3bqgyov3voh96"
CHECK_INTERVAL = 30  # seconds between checks
SEEN_TWEETS_FILE = "seen_tweets.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_seen_tweets():
    """Load previously seen tweet IDs from file"""
    if os.path.exists(SEEN_TWEETS_FILE):
        try:
            with open(SEEN_TWEETS_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()


def save_seen_tweets(seen_tweets):
    """Save seen tweet IDs to file"""
    with open(SEEN_TWEETS_FILE, 'w') as f:
        json.dump(list(seen_tweets), f)


async def send_to_discord(tweet_data):
    """Send tweet to Discord webhook"""
    try:
        embed = {
            "title": f"New tweet from @{TWITTER_USERNAME}",
            "description": tweet_data['text'][:4000],  # Discord limit
            "url": tweet_data['url'],
            "color": 1942002,  # Twitter blue
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Twitter Monitor"
            }
        }
        
        payload = {
            "embeds": [embed]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK, json=payload) as resp:
                if resp.status == 204:
                    logger.info(f"Sent to Discord: {tweet_data['url']}")
                    return True
                else:
                    logger.error(f"Discord webhook failed: {resp.status}")
                    return False
    except Exception as e:
        logger.error(f"Error sending to Discord: {e}")
        return False


async def send_pushover(tweet_data):
    """Send Pushover notification"""
    try:
        payload = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": tweet_data['text'][:1024],  # Pushover limit
            "title": f"@{TWITTER_USERNAME} tweeted",
            "url": tweet_data['url'],
            "url_title": "View on Twitter",
            "priority": 0,  # Normal priority (not loud)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.pushover.net/1/messages.json", data=payload) as resp:
                if resp.status == 200:
                    logger.info(f"Sent Pushover notification: {tweet_data['url']}")
                    return True
                else:
                    logger.error(f"Pushover failed: {resp.status}")
                    return False
    except Exception as e:
        logger.error(f"Error sending Pushover: {e}")
        return False


async def scrape_tweets():
    """Scrape latest tweets using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"Loading {TWITTER_URL}")
            await page.goto(TWITTER_URL, wait_until='networkidle', timeout=60000)
            
            # Wait for tweets to load
            await page.wait_for_timeout(3000)
            
            # Scroll a bit to load tweets
            await page.evaluate("window.scrollTo(0, 500)")
            await page.wait_for_timeout(2000)
            
            # Extract tweets
            tweets = await page.evaluate("""
                () => {
                    const tweetElements = document.querySelectorAll('article[data-testid="tweet"]');
                    const tweets = [];
                    
                    tweetElements.forEach(article => {
                        try {
                            // Get tweet text
                            const textElement = article.querySelector('[data-testid="tweetText"]');
                            const text = textElement ? textElement.innerText : '';
                            
                            // Get tweet link
                            const linkElement = article.querySelector('a[href*="/status/"]');
                            const href = linkElement ? linkElement.href : '';
                            
                            // Extract tweet ID from URL
                            const tweetId = href.match(/status\\/(\\d+)/)?.[1];
                            
                            // Get timestamp
                            const timeElement = article.querySelector('time');
                            const timestamp = timeElement ? timeElement.getAttribute('datetime') : '';
                            
                            if (tweetId && text) {
                                tweets.push({
                                    id: tweetId,
                                    text: text,
                                    url: href,
                                    timestamp: timestamp
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing tweet:', e);
                        }
                    });
                    
                    return tweets;
                }
            """)
            
            logger.info(f"Found {len(tweets)} tweets")
            return tweets
            
        except Exception as e:
            logger.error(f"Error scraping tweets: {e}")
            return []
        finally:
            await browser.close()


async def monitor_loop():
    """Main monitoring loop"""
    seen_tweets = load_seen_tweets()
    logger.info(f"Starting monitor for @{TWITTER_USERNAME}")
    logger.info(f"Already tracking {len(seen_tweets)} tweets")
    
    while True:
        try:
            tweets = await scrape_tweets()
            
            # Process tweets in reverse order (oldest first)
            new_tweets = []
            for tweet in reversed(tweets):
                if tweet['id'] not in seen_tweets:
                    new_tweets.append(tweet)
                    seen_tweets.add(tweet['id'])
            
            # Send notifications for new tweets
            for tweet in new_tweets:
                logger.info(f"New tweet detected: {tweet['id']}")
                await send_to_discord(tweet)
                await send_pushover(tweet)
                await asyncio.sleep(1)  # Small delay between notifications
            
            # Save seen tweets
            save_seen_tweets(seen_tweets)
            
            if new_tweets:
                logger.info(f"Processed {len(new_tweets)} new tweets")
            
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        
        # Wait before next check
        logger.info(f"Waiting {CHECK_INTERVAL} seconds...")
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(monitor_loop())

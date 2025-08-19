"""
Farcaster Invite Code Scraper
-----------------------------
A production-ready script to find Farcaster invite codes from public sources.
Author: GitHub Copilot
License: MIT
"""

import os
import re
import json
import logging
import sqlite3
import requests
import tweepy
import praw
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('farcaster_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
class Config:
    """Configuration class for storing API keys and settings."""
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
    
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = 'FarcasterInviteBot/1.0'
    
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    
    SEARCH_KEYWORDS = [
        "Farcaster invite code",
        "Farcaster invite link",
        "Farcaster invitation"
    ]
    
    # Regex pattern for Farcaster invite codes (alphanumeric, 8-12 chars)
    INVITE_CODE_PATTERN = r'\b[A-Za-z0-9]{8,12}\b'
    
    # Database settings
    DB_PATH = 'farcaster_codes.db'
    
    # Search interval in minutes
    SEARCH_INTERVAL = 10

class Database:
    """SQLite database manager for storing found invite codes."""
    
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.create_tables()
    
    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS invite_codes (
                    code TEXT PRIMARY KEY,
                    source TEXT,
                    found_at TIMESTAMP,
                    url TEXT,
                    is_valid BOOLEAN DEFAULT NULL
                )
            ''')
    
    def add_code(self, code: str, source: str, url: str):
        """Add a new invite code to the database if it doesn't exist."""
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT OR IGNORE INTO invite_codes (code, source, found_at, url)
                    VALUES (?, ?, ?, ?)
                ''', (code, source, datetime.now(), url))
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return False
    
    def is_code_exists(self, code: str) -> bool:
        """Check if a code already exists in the database."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM invite_codes WHERE code = ?', (code,))
        return cursor.fetchone() is not None

class NotificationService:
    """Service for sending notifications about new invite codes."""
    
    @staticmethod
    def send_telegram_notification(code: str, source: str, url: str):
        """Send notification via Telegram."""
        if not (Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID):
            return
        
        message = f"🎉 New Farcaster invite code found!\nCode: {code}\nSource: {source}\nURL: {url}"
        telegram_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        try:
            requests.post(telegram_url, json={
                'chat_id': Config.TELEGRAM_CHAT_ID,
                'text': message
            })
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")
    
    @staticmethod
    def send_discord_notification(code: str, source: str, url: str):
        """Send notification via Discord webhook."""
        if not Config.DISCORD_WEBHOOK_URL:
            return
            
        message = {
            "embeds": [{
                "title": "New Farcaster Invite Code Found! 🎉",
                "description": f"Code: `{code}`\nSource: {source}\nURL: {url}",
                "color": 5814783
            }]
        }
        
        try:
            requests.post(Config.DISCORD_WEBHOOK_URL, json=message)
        except Exception as e:
            logger.error(f"Discord notification error: {e}")

class InviteCodeScraper:
    """Main scraper class that coordinates all source-specific scrapers."""
    
    def __init__(self):
        self.db = Database()
        self.notification = NotificationService()
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize API clients."""
        # Twitter API setup
        if all([Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET,
                Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACCESS_SECRET]):
            auth = tweepy.OAuthHandler(Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET)
            auth.set_access_token(Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACCESS_SECRET)
            self.twitter_api = tweepy.API(auth)
        else:
            self.twitter_api = None
            logger.warning("Twitter API credentials not found")
        
        # Reddit API setup
        if Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_SECRET:
            self.reddit_api = praw.Reddit(
                client_id=Config.REDDIT_CLIENT_ID,
                client_secret=Config.REDDIT_CLIENT_SECRET,
                user_agent=Config.REDDIT_USER_AGENT
            )
        else:
            self.reddit_api = None
            logger.warning("Reddit API credentials not found")
    
    def extract_invite_codes(self, text: str) -> List[str]:
        """Extract potential invite codes from text using regex."""
        return re.findall(Config.INVITE_CODE_PATTERN, text)
    
    def process_found_code(self, code: str, source: str, url: str):
        """Process and store a newly found invite code."""
        if not self.db.is_code_exists(code):
            if self.db.add_code(code, source, url):
                logger.info(f"New code found: {code} from {source}")
                self.notification.send_telegram_notification(code, source, url)
                self.notification.send_discord_notification(code, source, url)
    
    def search_twitter(self):
        """Search Twitter for invite codes."""
        if not self.twitter_api:
            return
        
        try:
            for keyword in Config.SEARCH_KEYWORDS:
                tweets = self.twitter_api.search_tweets(q=keyword, lang="en", count=100)
                for tweet in tweets:
                    codes = self.extract_invite_codes(tweet.text)
                    for code in codes:
                        url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                        self.process_found_code(code, "Twitter", url)
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
    
    def search_reddit(self):
        """Search Reddit for invite codes."""
        if not self.reddit_api:
            return
        
        try:
            for keyword in Config.SEARCH_KEYWORDS:
                for submission in self.reddit_api.subreddit("all").search(keyword, limit=100):
                    # Search in submission title and body
                    text = f"{submission.title} {submission.selftext}"
                    codes = self.extract_invite_codes(text)
                    for code in codes:
                        self.process_found_code(code, "Reddit", submission.url)
                    
                    # Search in comments
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        codes = self.extract_invite_codes(comment.body)
                        for code in codes:
                            self.process_found_code(code, "Reddit", f"{submission.url}{comment.id}")
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
    
    def search_web(self):
        """Search Google and scrape web results for invite codes."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            for keyword in Config.SEARCH_KEYWORDS:
                search_url = f"https://www.google.com/search?q={keyword}"
                response = requests.get(search_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract and visit search result links
                for link in soup.find_all('a'):
                    url = link.get('href', '')
                    if url.startswith('http') and not any(domain in url for domain in ['google.com', 'twitter.com', 'reddit.com']):
                        try:
                            page_response = requests.get(url, headers=headers, timeout=10)
                            page_soup = BeautifulSoup(page_response.text, 'html.parser')
                            text = page_soup.get_text()
                            codes = self.extract_invite_codes(text)
                            for code in codes:
                                self.process_found_code(code, "Web", url)
                        except Exception as e:
                            logger.debug(f"Error scraping {url}: {e}")
        except Exception as e:
            logger.error(f"Web search error: {e}")
    
    def run_search(self):
        """Run all search methods."""
        logger.info("Starting search iteration...")
        self.search_twitter()
        self.search_reddit()
        self.search_web()
        logger.info("Search iteration completed")

def main():
    """Main function to initialize and run the scraper."""
    logger.info("Initializing Farcaster Invite Code Scraper...")
    
    # Create scraper instance
    scraper = InviteCodeScraper()
    
    # Create scheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(
        scraper.run_search,
        trigger=IntervalTrigger(minutes=Config.SEARCH_INTERVAL),
        next_run_time=datetime.now()  # Run immediately on start
    )
    
    try:
        logger.info(f"Scheduler started. Running every {Config.SEARCH_INTERVAL} minutes.")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        scheduler.shutdown()

if __name__ == "__main__":
    main()

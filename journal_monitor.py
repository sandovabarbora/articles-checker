import feedparser
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from dotenv import load_dotenv
from typing import List, Tuple, Dict
import time
import requests.exceptions

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('journal_monitor.log'),
        logging.StreamHandler()
    ]
)

JOURNAL_FEEDS = {
    "Journal of Machine Learning Research": "https://www.jmlr.org/jmlr.xml",
    "Machine Learning (Springer)": "https://link.springer.com/journal/10994.rss",
    "Data Mining and Knowledge Discovery": "https://link.springer.com/journal/10618.rss",
    "Big Data": "https://www.liebertpub.com/action/showFeed?ui=0&mi=3b6f4c&ai=si&jc=big",
    "Journal of Data Science": "https://jds-online.org/journal/JDS/issue/current/rss",
    "IEEE Transactions on Knowledge and Data Engineering": "https://ieeexplore.ieee.org/rss/TOC54.XML",
    "Nature Machine Intelligence": "https://www.nature.com/natmachintell.rss",
    "ACM Transactions on Intelligent Systems and Technology": "https://dl.acm.org/journal/tist/rss",
    "VLDB Journal": "https://link.springer.com/journal/778.rss",
    "ACM Transactions on Database Systems": "https://dl.acm.org/journal/tods/rss",
    "IEEE Transactions on Big Data": "https://ieeexplore.ieee.org/rss/TOC8054267.XML",
    "Information Systems (Elsevier)": "https://www.journals.elsevier.com/information-systems/rss",
    "Knowledge and Information Systems": "https://link.springer.com/journal/10115.rss",
    "Data & Knowledge Engineering": "https://www.journals.elsevier.com/data-and-knowledge-engineering/rss",
    
    # Additional journals
    "Journal of Artificial Intelligence Research": "https://www.jair.org/index.php/jair/gateway/plugin/WebFeedGatewayPlugin/rss2",
    "IEEE Transactions on Neural Networks and Learning Systems": "https://ieeexplore.ieee.org/rss/TOC5962385.XML",
    "Neural Computation (MIT Press)": "https://direct.mit.edu/neco/rss",
    "Pattern Recognition (Elsevier)": "https://www.journals.elsevier.com/pattern-recognition/rss",
    "Artificial Intelligence (Elsevier)": "https://www.journals.elsevier.com/artificial-intelligence/rss",
    "Journal of Statistical Software": "https://www.jstatsoft.org/index.php/jss/gateway/plugin/WebFeedGatewayPlugin/rss2",
    "ACM Transactions on Knowledge Discovery from Data": "https://dl.acm.org/journal/tkdd/rss",
    "Data Science and Engineering (Springer)": "https://link.springer.com/journal/41019.rss",
    "International Journal of Data Science and Analytics": "https://link.springer.com/journal/41060.rss",
    "Journal of Big Data": "https://journalofbigdata.springeropen.com/articles/most-recent/rss"
}

# Constants
ARTICLE_STORE = "seen_articles.json"
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds

class JournalMonitor:
    def __init__(self):
        load_dotenv()
        self.email_sender = os.getenv("EMAIL_SENDER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_receiver = os.getenv("EMAIL_RECEIVER")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        
        if not all([self.email_sender, self.email_password, self.email_receiver]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

    def load_seen_articles(self) -> Dict:
        """Load previously seen articles from JSON file with error handling."""
        try:
            if os.path.exists(ARTICLE_STORE):
                with open(ARTICLE_STORE, "r", encoding='utf-8') as file:
                    return json.load(file)
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Error reading JSON file: {e}")
            return {}

    def save_seen_articles(self, seen_articles: Dict) -> None:
        """Save seen articles to JSON file with error handling."""
        try:
            with open(ARTICLE_STORE, "w", encoding='utf-8') as file:
                json.dump(seen_articles, file, indent=4, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Error saving articles: {e}")

    def fetch_feed(self, url: str, retries: int = RETRY_ATTEMPTS) -> feedparser.FeedParserDict:
        """Fetch RSS feed with retry mechanism."""
        for attempt in range(retries):
            try:
                return feedparser.parse(url)
            except Exception as e:
                if attempt == retries - 1:
                    logging.error(f"Failed to fetch feed after {retries} attempts: {e}")
                    return feedparser.FeedParserDict()
                time.sleep(RETRY_DELAY)
        return feedparser.FeedParserDict()

    def fetch_new_articles(self) -> List[Tuple[str, str, str]]:
        """Fetch latest articles from RSS feeds with improved error handling."""
        seen_articles = self.load_seen_articles()
        new_articles = []

        for journal, url in JOURNAL_FEEDS.items():
            logging.info(f"Checking feed: {journal}")
            feed = self.fetch_feed(url)

            if not feed.entries:
                logging.warning(f"No entries found for {journal}")
                continue

            if journal not in seen_articles:
                seen_articles[journal] = []

            for entry in feed.entries:
                try:
                    article_title = entry.title.strip()
                    article_link = entry.link.strip()

                    if article_title not in seen_articles[journal]:
                        new_articles.append((journal, article_title, article_link))
                        seen_articles[journal].append(article_title)
                        logging.info(f"New article found: {article_title}")
                except AttributeError as e:
                    logging.error(f"Error processing entry in {journal}: {e}")

        self.save_seen_articles(seen_articles)
        return new_articles

    def send_email(self, new_articles: List[Tuple[str, str, str]]) -> None:
        """Send an email notification with improved formatting and error handling."""
        if not new_articles:
            logging.info("No new articles to send")
            return

        subject = f"New Journal Articles Available - {datetime.now().strftime('%Y-%m-%d')}"
        body = "Here are the latest articles:\n\n"

        # Group articles by journal
        articles_by_journal = {}
        for journal, title, link in new_articles:
            if journal not in articles_by_journal:
                articles_by_journal[journal] = []
            articles_by_journal[journal].append((title, link))

        # Create formatted email body
        for journal, articles in articles_by_journal.items():
            body += f"\n{journal}:\n"
            for title, link in articles:
                body += f"- {title}\n  {link}\n"

        msg = MIMEMultipart()
        msg["From"] = self.email_sender
        msg["To"] = self.email_receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
            logging.info(f"Email notification sent with {len(new_articles)} articles")
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            raise

def main():
    """Main function with error handling."""
    try:
        monitor = JournalMonitor()
        logging.info("Starting journal monitor...")
        new_articles = monitor.fetch_new_articles()
        monitor.send_email(new_articles)
        logging.info("Journal monitor completed successfully")
    except Exception as e:
        logging.error(f"Critical error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
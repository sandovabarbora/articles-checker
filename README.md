# Academic Journal Monitor

A Python script that monitors multiple academic journals' RSS feeds for new articles and sends email notifications when new articles are published. This tool is particularly useful for researchers and academics who want to stay updated with the latest publications in machine learning, data science, and artificial intelligence.

## Features

- Monitors RSS feeds from 25+ leading academic journals
- Sends formatted email notifications for new articles
- Keeps track of previously seen articles to avoid duplicates
- Implements robust error handling and logging
- Includes retry mechanism for failed RSS feed fetches
- Groups articles by journal in email notifications

## Supported Journals

The script currently monitors journals including:
- Journal of Machine Learning Research
- Nature Machine Intelligence
- IEEE Transactions on Knowledge and Data Engineering
- Machine Learning (Springer)
- Journal of Artificial Intelligence Research
- And many more...

## Prerequisites

- Python 3.6+
- Required Python packages:
  - feedparser
  - python-dotenv
  - typing
  - requests

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install feedparser python-dotenv requests
```

3. Create a `.env` file in the project directory with the following variables:
```
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password
EMAIL_RECEIVER=recipient-email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Configuration

### Email Settings
- The script uses SMTP to send emails
- Default SMTP server is Gmail (smtp.gmail.com)
- Default port is 587 (TLS)
- If using Gmail, you'll need to create an App Password if 2FA is enabled

### Logging
- Logs are written to `journal_monitor.log`
- Includes both file and console logging
- Log level is set to INFO by default

### Article Storage
- Seen articles are stored in `seen_articles.json`
- The file is created automatically on first run

## Usage

Run the script with:
```bash
python journal_monitor.py
```

The script will:
1. Load previously seen articles
2. Check all configured RSS feeds for new articles
3. Send an email if new articles are found
4. Update the seen articles database
5. Log all activities

## Error Handling

The script includes comprehensive error handling for:
- RSS feed connection issues
- Email sending failures
- File I/O operations
- JSON parsing errors
- Missing environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Author

Barbora Sandova

## Acknowledgments

- Thanks to all the academic journals providing RSS feeds
- Built using Python and various open-source libraries
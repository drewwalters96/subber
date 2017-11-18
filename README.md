# Subber
Subber is a web-based application that allows active reddit users to discover subreddits based on post history and subscription data.

## Quick Start Guide
Add Reddit API credentials to `subber.cfg`
```bash
mv subber/subber.cfg.example subber/subber.cfg
vim subber/subber.cfg
```

Install project dependencies
```bash
pip install -r requirements.txt
```

Start REST API
```bash
cd subber
gunicorn server:api
```

Request subreddit recommendations for a user
```bash
curl 127.0.0.1:8000/user/{REDDIT-USERNAME}
```

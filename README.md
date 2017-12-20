# Subber

[![BuildStatus](https://travis-ci.org/drewwalters96/subber.svg?branch=master)](
https://travis-ci.org/drewwalters96/subber)

Subber is a web-based application that allows active reddit users to discover
subreddits based on post history and subscription data.

## Quick Start Guide

Add Reddit API credentials to `subber.cfg`

```bash
mv subber.cfg.example subber.cfg
vim subber.cfg
```

Install project dependencies and package for Python 3

```bash
pip3 install -r requirements.txt
pip3 install .
```

Start REST API with timeout value

```bash
gunicorn subber.app:api -t 900
```

Request subreddit recommendations for a user

```bash
curl 127.0.0.1:8000/user/{REDDIT-USERNAME}
```

## Troubleshooting

If a runtime error occurs while Subber is running, Subber will terminate and
log detailed error messages in `subber.log`. If more details are not available,
please file an issue on the Subber
[issues page](https://github.com/drewwalters96/subber/issues) along with a copy
of your `subber.log` file.

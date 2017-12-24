# Subber

[![BuildStatus](https://travis-ci.org/drewwalters96/subber.svg?branch=master)](
https://travis-ci.org/drewwalters96/subber)
[![Docker Repository on
Quay](https://quay.io/repository/drewwalters96/subber/status "Docker Repository
on Quay")](https://quay.io/repository/drewwalters96/subber)

Subber is a web-based application that allows active reddit users to discover
subreddits based on post history and subscription data.

## Quick Start Guide

To deploy Subber, you must obtain an API key and application ID.

1. Go to your [Reddit authorized apps](https://www.reddit.com/prefs/apps/)
   page.
2. Click the "are you a developer? create an app..." button at the bottom of the
   page.
3. Fill out the form with the appropriate details, ensuring that `script` is
   selected.

After submitting the form, add your Reddit API credentials to `subber.cfg`.

```bash
# Move and edit example config
cp subber.cfg.example subber.cfg
vi subber.cfg
```

### Run Subber in a container (recommended)

In order to run Subber in a container, you must have
[Docker](https://www.docker.com/get-docker) installed.

Pull the Subber Docker image:

**NOTE:** *Depending on your platform, you may need to run Docker with root
privileges.*

```bash
docker pull quay.io/drewwalters96/subber
```

Run the subber container with mounted Subber config file:

```bash
docker run --name subber -dp 8000:8000 -v $PWD/subber.cfg:/subber/subber.cfg \
quay.io/drewwalters96/subber:latest
```

The Subber container is now running in detached mode and is ready for usage
(see the "Using Subber" section for more details).

To stop the container, execute:

```bash
docker stop subber
docker rm subber
```

### Run Subber as a Python package (for developers)

Install project dependencies and package for Python 3:

```bash
pip3 install -r requirements.txt
pip3 install .
```

Start REST API with timeout value:

```bash
gunicorn subber.subber:app -t 900
```

### Using Subber

Request subreddit recommendations for a user by opening your browser and
visiting [127.0.0.1:8000](http://127.0.0.1:8000).

**NOTE:** *This may take a few moments.*

## Troubleshooting

If a runtime error occurs while Subber is running, Subber will terminate and
log detailed error messages in `subber.log`. If more details are not available,
please file an issue on the Subber
[issues page](https://github.com/drewwalters96/subber/issues) along with a copy
of your `subber.log` file.

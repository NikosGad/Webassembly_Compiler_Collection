# Base Python Image
FROM python:3.8-slim-buster

# Set application dedicated /app directory as working directory
WORKDIR /app

# Manage package versions and python dependencies
# With update, a list of packages gets downloaded and stored in /var/lib/apt/lists/
# Documentation files in /usr/share/doc/* can be deleted (they appear when a related package upgrades)
COPY requirements.txt requirements.txt
RUN set -ex\
 && apt-get update\
 && apt-get install -y gcc\
 && pip install -r requirements.txt\
 && rm -f requirements.txt\
 && apt-get purge -y --auto-remove gcc\
 && rm -rf /var/lib/apt/lists/*\
 && rm -rf /usr/share/doc/*

# Install the application code
COPY rest_server.py rest_server.py
COPY uwsgi.ini ./uwsgi.ini

# Manage code base ownership
RUN groupadd -g 1000 server \
&& useradd -u 1000 -g 1000 server

RUN chown server:server rest_server.py \
 && chmod 400 rest_server.py

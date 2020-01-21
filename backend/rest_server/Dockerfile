# Base Python Image
FROM python:3.8

# Set application dedicated /app directory as working directory
WORKDIR /app

# Manage package versions and python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm -f requirements.txt

# Install the application code
COPY rest_server.py rest_server.py
COPY wsgi.py wsgi.py
COPY uwsgi.ini ./uwsgi.ini

# Manage code base ownership
RUN groupadd -g 1000 server \
&& useradd -u 1000 -g 1000 server

RUN chown server:server rest_server.py \
 && chmod 400 rest_server.py

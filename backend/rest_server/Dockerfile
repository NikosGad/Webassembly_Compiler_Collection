FROM trzeci/emscripten-slim:sdk-tag-1.39.4-64bit as emscriptensdk

# Base Python Image
FROM python:3.8-slim-buster

# For more info on multi stage build to extend emscripten-slim with changing
# base image, visit: https://hub.docker.com/r/trzeci/emscripten-slim
COPY --from=emscriptensdk /emsdk_portable /emsdk_portable

# Set emscripten specific environment variables to maintain the entrypoint from
# base image
ENV EMSDK /emsdk_portable
ENV EMSCRIPTEN=${EMSDK}/emscripten/sdk

ENV EM_DATA ${EMSDK}/.data
ENV EM_CONFIG ${EMSDK}/.emscripten
ENV EM_CACHE ${EM_DATA}/cache
ENV EM_PORTS ${EM_DATA}/ports

# Expose tools to system PATH
ENV PATH="${EMSDK}:${EMSDK}/emscripten/sdk:${EMSDK}/llvm/clang/bin:${EMSDK}/node/current/bin:${EMSDK}/binaryen/bin:${PATH}"

# Golang Installation
RUN set -ex\
 && apt-get update\
 && apt-get install -y wget\
 && wget -O /go.tgz "https://golang.org/dl/go1.13.7.linux-amd64.tar.gz"\
 && echo "b3dd4bd781a0271b33168e627f7f43886b4c5d1c794a4015abf34e99c6526ca3 */go.tgz" | sha256sum -c -\
 && tar -xzf /go.tgz -C /usr/local\
 && rm /go.tgz\
 && apt-get purge -y --auto-remove wget\
 && rm -rf /var/lib/apt/lists/*\
 && rm -rf /usr/share/doc/*

ENV GOPATH /results/go
ENV PATH="$GOPATH/bin:/usr/local/go/bin:$PATH"

# Set application dedicated /app directory as working directory
WORKDIR /app

COPY uwsgi.ini ./uwsgi.ini

# Manage package versions and python dependencies
# With update, a list of packages gets downloaded and stored in /var/lib/apt/lists/
# Documentation files in /usr/share/doc/* can be deleted (they appear when a related package upgrades)
COPY requirements.txt requirements.txt
RUN set -ex\
 && apt-get update\
 && apt-get install -y gcc libpq-dev\
 && pip install -r requirements.txt\
 && rm -f requirements.txt\
 && apt-get purge -y --auto-remove gcc\
 && rm -rf /var/lib/apt/lists/*\
 && rm -rf /usr/share/doc/*

# Install the application code
COPY rest_server/ rest_server/
COPY wsgi.py wsgi.py
COPY database_accepts_connections.py database_accepts_connections.py

# Manage code base ownership
RUN groupadd -g 1000 server \
&& useradd -u 1000 -g 1000 -d /dev/null -s /usr/bin/nologin -c "This user runs the server" server

RUN chown server:server wsgi.py database_accepts_connections.py\
 && chmod 400 wsgi.py database_accepts_connections.py

RUN chown server:server -R rest_server\
 && chmod 400 -R rest_server\
 && chmod 500 rest_server rest_server/compile rest_server/models rest_server/views

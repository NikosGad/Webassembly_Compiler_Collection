FROM node:13.6.0

RUN npm install -g @angular/cli@8.3.23

WORKDIR /home/node/app-frontend

# This is used to make node user the owner instead of root
RUN mkdir node_modules && chown -R node:node /home/node/app-frontend/node_modules

USER node

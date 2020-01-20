# docker build -t angular_cli:latest .
# docker run -it --rm --name angular_cli_devel -v /home/nikos/HMMY\ EMP/Diploma\ Thesis/Webassembly_Compiler_Collection/frontend/app-frontend:/home/node/app-frontend -v /home/node/app-frontend/node_modules -p 4200:4200 angular_cli:latest bash
FROM node:13.6.0

RUN npm install -g @angular/cli@8.3.23

##### These commands should be commented out if there is no angular project created yet #####
COPY ./app-frontend/package.json /home/node/app-frontend/package.json
COPY ./app-frontend/package-lock.json /home/node/app-frontend/package-lock.json

WORKDIR /home/node/app-frontend

# This is used to make node user the owner instead of root
RUN mkdir node_modules && chown -R node:node /home/node/app-frontend/node_modules

RUN npm install
#####

USER node

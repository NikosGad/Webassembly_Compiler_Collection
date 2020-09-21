# Webassembly_Compiler_Collection
This is a compiler collection for Webassembly.

The project is developed as a Proof of Concept (PoC) for my Diploma Thesis as Electrical and Computer Engineer at National Technical University of Athens, Greece.

It is developed using Angular 8 for the frontend, Python 3 (Flask) for the backend and PostgreSQL 12 for the database server. It also uses technologies, like NGINX, uWSGI and Docker Containers. Thus, both deployment and scaling are fast and easy.

### Supported Languages
- C/C++ (emscripten 1.39.4)
- Golang (1.13.7)

### Deployment Dependencies
The necessary dependencies are the following:
- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose](https://docs.docker.com/compose/install/) (a release that supports [version 3 compose Files](https://docs.docker.com/compose/compose-file/))

Follow the above installation notes to prepare the dependencies in your system.

### Deployment Steps
1) Clone the repo!
2) Change the first 8 lines inside the [.env](https://github.com/NikosGad/Webassembly_Compiler_Collection/blob/master/.env) file (https://github.com/NikosGad/Webassembly_Compiler_Collection/blob/21256f84d435647282552f7534a0f9d5fbc752db/.env#L1-L8). These lines contain dummy values as placeholders.

Variables Explanation:<br>
SYSTEM_IP: Your system's Public Floating IP (necessary change)<br>
FRONTEND_HOST_PORT: Port on host system where the frontend is available (non-necessary change)<br>
BACKEND_HOST_PORT: Port on host system where the backend is available (non-necessary change)<br>
HOST_RESULTS_DIR_PREFIX: Directory path on Host's File System where the container volumes are placed (the directory path should exist and it would be better if it is empty (necessary change)<br>
POSTGRES_PASSWORD: Database Password (necessary change - security reasons)<br>
POSTGRES_USER: Database User (non-necessary change, in case of a change then it must occur before the first deployment)<br>
JWT_SECRET_KEY: A secret key for JWT signature (necessary change)

3) Run "sudo bash deploy.sh --build" to build the images
4) Run "sudo bash deploy.sh –-deploy" to deploy

### Remove Deployment
Remove an existing deployment by running "sudo bash deploy.sh --deploy-down"

### Other Options
You can always experiment and use the docker-compose files to adjust the app on your needs! :)

FROM postgres:12.2

RUN groupadd -g 1000 database\
 && useradd -u 1000 -g 1000 -d /var/lib/postgresql -s /bin/bash -c "Non-privileged user that runs the database" database

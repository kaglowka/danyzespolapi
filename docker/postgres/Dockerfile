FROM postgres:10.4

RUN mkdir /backups
RUN mkdir /patches

ADD ./database/patches /patches

ADD ./docker/postgres/init-mcod-db.sh /docker-entrypoint-initdb.d/init-user-db.sh

COPY ./docker/postgres/backup.sh /usr/local/bin/backup
RUN chmod +x /usr/local/bin/backup

COPY ./docker/postgres/restore.sh /usr/local/bin/restore
RUN chmod +x /usr/local/bin/restore

COPY ./docker/postgres/list-backups.sh /usr/local/bin/list-backups
RUN chmod +x /usr/local/bin/list-backups

RUN echo "myapp.userid='1'" >> /var/lib/postgresql/data/postgresql.conf

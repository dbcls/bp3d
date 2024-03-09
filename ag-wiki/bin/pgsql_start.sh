#!/bin/csh

source ./env.sh

${PGSQL}/bin/pg_ctl -D ${PGDATA} -o "-p ${PORT}" -l ${PGDATA}/log.txt start

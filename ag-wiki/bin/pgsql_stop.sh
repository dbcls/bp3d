#!/bin/csh

source ./env.sh

${PGSQL}/bin/pg_ctl -D ${PGDATA} stop

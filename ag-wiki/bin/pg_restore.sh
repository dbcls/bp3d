#!/bin/csh

source ./env.sh

${PGSQL}/bin/psql -p ${PORT} -U ${PGUSER} ${DBNAME} < tree.dmp

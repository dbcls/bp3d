#!/bin/bash

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/psql -p $PORT -U $PGUSER $DBNAME

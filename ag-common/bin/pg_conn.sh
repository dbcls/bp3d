#!/bin/bash

cd `dirname $0`

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/psql -p $PORT -U $PGUSER $DBNAME

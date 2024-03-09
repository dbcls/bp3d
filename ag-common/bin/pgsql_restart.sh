#!/bin/bash

cd `dirname $0`

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/pg_ctl -D $PGDATA -o "-p $PORT" -m f -l $PGDATA/log.txt restart

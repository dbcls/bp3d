#!/bin/bash

cd `dirname $0`

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/createdb -p $PORT -U $PGUSER $DBNAME

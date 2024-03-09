#!/bin/bash

cd `dirname $0`

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/initdb -D $PGDATA -U $PGUSER

#!/bin/bash

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/pg_ctl stop  -D $PGDATA -m fast

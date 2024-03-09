#!/bin/bash

#$PGSQL/bin/dropdb -p $PORT -U $PGUSER $DBNAME
#$PGSQL/bin/createdb -p $PORT -U $PGUSER $DBNAME
#$PGSQL/bin/pg_restore -p $PORT -U $PGUSER -d $DBNAME "$DBNAME.dump"

#DATE=`date +'%y%m%d'`

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/pg_dump -p $PORT -U $PGUSER --create -Fc -i $DBNAME > "$DBNAME.dump"

#!/bin/bash

cd `dirname $0`

[ -e ./env.sh ] && . ./env.sh

$PGSQL/bin/psql -p $PORT -U $PGUSER $DBNAME -f /bp3d/local/pgsql/share/pgsenna2.sql
$PGSQL/bin/psql -p $PORT -U $PGUSER $DBNAME -f /bp3d/local/pgsql/share/contrib/dblink.sql
zcat ../ag_common_130930.dump.gz | $PGSQL/bin/psql -p $PORT -U $PGUSER $DBNAME
$PGSQL/bin/psql -p $PORT -U $PGUSER $DBNAME -f delete_sql.txt

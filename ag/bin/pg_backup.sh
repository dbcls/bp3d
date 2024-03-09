#!/bin/bash

cd `dirname $0`

#$PGSQL/bin/dropdb -p $PORT -U $PGUSER $DBNAME
#$PGSQL/bin/createdb -p $PORT -U $PGUSER $DBNAME
#$PGSQL/bin/pg_restore -p $PORT -U $PGUSER -d $DBNAME "$DBNAME.dump"

DATE=`date +'%y%m%d'`

[ -e ./env.sh ] && . ./env.sh

#$PGSQL/bin/pg_dump -p $PORT -U $PGUSER --create -Fc -i $DBNAME > "$AG_HOME/$AG_NUM/db_backup/$DBNAME.$DATE.dump"

BACKUP_FILE="$AG_HOME/$AG_NUM/db_backup/$DBNAME.$DATE.dump.gz"

sigint () {
	echo "trap INT or TERM"
	[ -f ${BACKUP_FILE} ] && rm -fr ${BACKUP_FILE}
}
if [ ! -f ${BACKUP_FILE} -o ! -s ${BACKUP_FILE} ]; then
	trap sigint INT TERM
	$PGSQL/bin/pg_dump -p ${PORT} -U ${PGUSER} -C ${DBNAME} | gzip > ${BACKUP_FILE}
	RETVAL=$?
	if [ $RETVAL -ne 0 ]; then
		sigint
		exit $ret
	fi
fi

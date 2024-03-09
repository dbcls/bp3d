#!/bin/bash

cd `dirname $0`

#$PGSQL/bin/dropdb -p $PORT -U $PGUSER $DBNAME
#$PGSQL/bin/createdb -p $PORT -U $PGUSER $DBNAME
#$PGSQL/bin/pg_restore -p $PORT -U $PGUSER -d $DBNAME "$DBNAME.dump"

DATE=`date +'%Y%m%d'`
AGO_DATE=`date +'%Y%m%d' -d '1 day ago'`

[ -e ./env.sh ] && . ./env.sh

#$PGSQL/bin/pg_dump -p $PORT -U $PGUSER --create -Fc -i $DBNAME > "$AG_HOME/$AG_NUM/db_backup/$DBNAME.$DATE.dump"

BACKUP_FILE="$AG_HOME/$AG_NUM/db_backup/$DBNAME.$DATE.dump.gz"
AGO_BACKUP_FILE="$AG_HOME/$AG_NUM/db_backup/$NEW_DBNAME.$AGO_DATE.dump.gz"

sigint () {
	echo "trap INT or TERM"
	[ -f ${BACKUP_FILE} ] && rm -fr ${BACKUP_FILE}
	[ -f ${AGO_BACKUP_FILE} ] && rm -fr ${AGO_BACKUP_FILE}
}
ago_sigint () {
	echo "trap INT or TERM"
	[ -f ${AGO_BACKUP_FILE} ] && rm -fr ${AGO_BACKUP_FILE}
}
if [ ! -f ${BACKUP_FILE} -o ! -s ${BACKUP_FILE} ]; then
	trap sigint INT TERM
	nice -n 19 $PGSQL/bin/pg_dump -p ${PORT} -U ${PGUSER} -o -O ${DBNAME} | nice -n 19 gzip > ${BACKUP_FILE}
	RETVAL=$?
	if [ $RETVAL -ne 0 ]; then
		sigint
		exit $ret
	fi
	chmod 0400 ${BACKUP_FILE}
	trap '' INT TERM
fi
if [ ! -f ${AGO_BACKUP_FILE} -o ! -s ${AGO_BACKUP_FILE} ]; then
	trap ago_sigint INT TERM
	nice -n 19 $PGSQL/bin/pg_dump -p ${PORT} -U ${PGUSER} -o -O ${NEW_DBNAME} | nice -n 19 gzip > ${AGO_BACKUP_FILE}
	RETVAL=$?
	if [ $RETVAL -ne 0 ]; then
		ago_sigint
		exit $ret
	fi
	chmod 0400 ${AGO_BACKUP_FILE}
	trap '' INT TERM
fi

#!/bin/bash

CD_DIR=`dirname $0`/../logs/`date --date "1day ago" +%Y/%m`
GZIP_DIR=`date --date "1day ago" +%d`
#GZIP_DIR=`date +%d`
#GZIP=/bin/gzip
TAR=/bin/tar
RM=/bin/rm
#echo ${CD_DIR}
#echo `pwd`
#echo ${GZIP_DIR}
if [ -d ${CD_DIR} ]; then
	cd ${CD_DIR}
	if [ -d ${GZIP_DIR} ]; then
#		echo ${GZIP_DIR}
		${TAR} cfz ${GZIP_DIR}.tar.gz ${GZIP_DIR} && ${RM} -fr ${GZIP_DIR} &
	fi
fi

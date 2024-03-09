#!/bin/bash

export LANG=C

cd `dirname $0`

export PYTHONPATH="/bp3d/local/VTK/lib/python2.6/site-packages"
export PERL5LIB="/bp3d/ag-test/htdocs:/bp3d/ag-test/htdocs/API:/bp3d/ag-test/htdocs/API/lib:/bp3d/ag-test/lib:/bp3d/ag-common/lib"

export AG_DB_HOST=127.0.0.1
export AG_DB_PORT=8543

DATE=`/bin/date +'%Y/%m/%d'`

P_MCA=/bp3d/MappingManager/cron/make_mca_image.pl
P_MCA_BASENAME=`/bin/basename ${P_MCA}`
P_MCA_DIRNAME=`/bin/basename ${P_MCA} .pl`

/usr/bin/killall ${P_MCA_BASENAME} 2>/dev/null
P_MCA_RETVAL=$?
if [ ${P_MCA_RETVAL} -eq 0 ]; then
	/bin/sleep 60
fi

/bin/nice -n 19 /bin/find mca_images/ -type d -name "*.lock" -exec rm -fr {} \; 1>/dev/null 2>&1

#env|sort
#exit

LOGDIR=logs/${DATE}
/bin/mkdir -p ${LOGDIR}
#exit;

P_UPD=/bp3d/MappingManager/batch/update_concept_art_map_modified.pl
P_UPD_DIRNAME=`/bin/basename ${P_UPD} .pl`
/bin/nice -n 19 ${P_UPD} 1> ${LOGDIR}/${P_UPD_DIRNAME}.log 2>&1
#/bin/nice -n 19 ${P_UPD}

/bin/nice -n 19 ${P_MCA} 1> ${LOGDIR}/${P_MCA_DIRNAME}.log 2>&1 &

exit 0

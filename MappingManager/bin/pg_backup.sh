#!/bin/bash

BASENAME=`basename $0 ".sh"`
cd `dirname $0`
DIRNAME=`pwd`
[ -e ./env.sh ] && . ./env.sh

#echo `env`
#echo ${PYTHONPATH}
#echo ${LD_LIBRARY_PATH}


WORK_HOME="$AG_HOME/$AG_NUM"
DATE=`date +'%Y%m%d'`
BACKUP_DATE=`date +'%Y%m01'`
BACKUP_FILE="${WORK_HOME}/db_backup/$DBNAME.${BACKUP_DATE}.dump.gz"

AG_DUMP_DATETIME=`date '+%Y%m%d-%H%M%S'`
#AG_DUMP_DATE=`date '+%Y%m%d'`
AG_DUMP_DATE=`date '+%Y%m01'`
AG_DUMP_FILE=${AG_HOME}/ag1/db_backup/${AG_DBNAME}.${AG_DUMP_DATETIME}.dump.gz
AG_DUMP_SUMLINK=${AG_HOME}/ag1/db_backup/${AG_DBNAME}.${AG_DUMP_DATE}.dump.gz

CB_IDS=(24 25)
TRIO_FILES=(/opt/services/ag/FMA/fma_4.12.0/fma_4.12.0_trio_bp3d.txt /opt/services/ag/FMA/fma_5.0.0/fma_5.0.0_trio_bp3d.txt)
AG_CB_IDS=(20 21)
AG_DATASET_NAMES=(il412 il500)

CB_ID_SIZE=${#CB_IDS[*]}

NICE="nice -n 19"
PSQL="${NICE} ${PGBIN}/psql -p ${PGPORT} -U ${PGUSER}"
PG_DUMP="${NICE} $PGHOME/bin/pg_dump -p ${PGPORT} -U ${PGUSER} -O"
GZIP="${NICE} gzip"
ZCAT="${NICE} zcat"
RSYNC="${NICE} rsync -avPh"

LOGFILE="${DIRNAME}/logs/${BASENAME}.${DATE}.txt"
echo "" > ${LOGFILE}
logs(){
	local MSG=$1
	local LOGDATE=$(date "+%Y/%m/%d %H:%M:%S")
	echo "[${LOGDATE}][${BASH_LINENO}] - [${MSG}]" 1>>${LOGFILE} 2>&1
}

#一ケ月前から更新があったの確認
START_DATE=`date '+%Y%m01' -d "1 month ago"`
START_DATETIME=`date '+%Y-%m-01 00:00:00' -d "1 month ago"`
END_DATE=`date '+%Y%m01'`
END_DATETIME=`date '+%Y-%m-01 00:00:00'`

SQL_CONCEPT_ART_MAP="SELECT count(cm_entry) FROM concept_art_map WHERE cm_entry>='${START_DATETIME}' AND cm_entry<'${END_DATETIME}';"
SQL_CONCEPT_SYNONYM="SELECT count(cs_entry) FROM concept_synonym WHERE cs_entry>='${START_DATETIME}' AND cs_entry<'${END_DATETIME}';"
SQL_CONCEPT_DATA_SYNONYM="SELECT count(cds_entry) FROM concept_data_synonym WHERE cds_entry>='${START_DATETIME}' AND cds_entry<'${END_DATETIME}';"
SQL_ART_FILE="SELECT count(art_entry) FROM art_file WHERE art_entry>='${START_DATETIME}' AND art_entry<'${END_DATETIME}';"

RAW_COUNT_CONCEPT_ART_MAP=`${PSQL} -d ${DBNAME} -x -t -A -c "${SQL_CONCEPT_ART_MAP}"`
RAW_COUNT_CONCEPT_SYNONYM=`${PSQL} -d ${DBNAME} -x -t -A -c "${SQL_CONCEPT_SYNONYM}"`
RAW_COUNT_CONCEPT_DATA_SYNONYM=`${PSQL} -d ${DBNAME} -x -t -A -c "${SQL_CONCEPT_DATA_SYNONYM}"`
RAW_COUNT_ART_FILE=`${PSQL} -d ${DBNAME} -x -t -A -c "${SQL_ART_FILE}"`

DATA_COUNT_CONCEPT_ART_MAP=${RAW_COUNT_CONCEPT_ART_MAP#count|}
DATA_COUNT_CONCEPT_SYNONYM=${RAW_COUNT_CONCEPT_SYNONYM#count|}
DATA_COUNT_CONCEPT_DATA_SYNONYM=${RAW_COUNT_CONCEPT_DATA_SYNONYM#count|}
DATA_COUNT_ART_FILE=${RAW_COUNT_ART_FILE#count|}

logs "DATA_COUNT_CONCEPT_ART_MAP=[${DATA_COUNT_CONCEPT_ART_MAP}]"
logs "DATA_COUNT_CONCEPT_SYNONYM=[${DATA_COUNT_CONCEPT_SYNONYM}]"
logs "DATA_COUNT_CONCEPT_DATA_SYNONYM=[${DATA_COUNT_CONCEPT_DATA_SYNONYM}]"
logs "DATA_COUNT_ART_FILE=[${DATA_COUNT_ART_FILE}]"

FMASEARCH_BASEHOME="$AG_HOME/FMASearch_SegmentUI"
OLD_FMASEARCH_HOME="${FMASEARCH_BASEHOME}/${START_DATE}"
NEW_FMASEARCH_HOME="${FMASEARCH_BASEHOME}/${END_DATE}"

#echo "${OLD_FMASEARCH_HOME}"
#echo "${NEW_FMASEARCH_HOME}"
#exit 1;

if [ ${DATA_COUNT_CONCEPT_ART_MAP} -eq 0 ] && [ ${DATA_COUNT_CONCEPT_SYNONYM} -eq 0 ] &&  [ ${DATA_COUNT_CONCEPT_DATA_SYNONYM} -eq 0 ] &&  [ ${DATA_COUNT_ART_FILE} -eq 0 ]; then
	logs "None update data"
	if [ ! -d ${NEW_FMASEARCH_HOME} ]; then
		cd ${FMASEARCH_BASEHOME} && ln -s ${START_DATE} ${END_DATE}
	fi
	exit 1
fi


#一ケ月前の日付
AG_DUMP_MONTH_AGO_DATE=`date '+%Y%m01' -d "1 month ago"`
#一ケ月前のAG_DBNAMEのバックアップファイル
AG_DUMP_MONTH_AGO_FILE=${AG_HOME}/ag1/db_backup/${AG_DBNAME}.${AG_DUMP_MONTH_AGO_DATE}.dump.gz

if [ ! -f ${AG_DUMP_MONTH_AGO_FILE} -o ! -s ${AG_DUMP_MONTH_AGO_FILE} ]; then
	logs "Unknown file [${AG_DUMP_MONTH_AGO_FILE}]"
	exit 1
fi

sigint () {
	logs "trap INT or TERM"
	[ -f ${BACKUP_FILE} ] && rm -fr ${BACKUP_FILE}
}

#最新環境をバックアップ
if [ ! -f ${BACKUP_FILE} -o ! -s ${BACKUP_FILE} ]; then
	trap sigint INT TERM
	${PG_DUMP} ${DBNAME} | ${GZIP} > ${BACKUP_FILE}
	RETVAL=$?
	if [ $RETVAL -ne 0 ]; then
		sigint
		exit $RETVAL
	fi
	chmod 0400 ${BACKUP_FILE}
	trap '' INT TERM
	exit 0
fi

#AG_DBNAME_TESTにデータをリストア
DEV_AG_DBNAME_TEST="${AG_DBNAME_TEST}_${DATE}"
#<< COMMENTOUT
SQL="DROP DATABASE IF EXISTS ${DEV_AG_DBNAME_TEST}"
logs "${SQL}"
${PSQL} -c "${SQL}" 1>>${LOGFILE} 2>&1
RETVAL=$?
[ $RETVAL -ne 0 ] && exit $RETVAL

SQL="CREATE DATABASE ${DEV_AG_DBNAME_TEST}"
logs "${SQL}"
${PSQL} -c "${SQL}" 1>>${LOGFILE} 2>&1
RETVAL=$?
[ $RETVAL -ne 0 ] && exit $RETVAL

logs "${ZCAT} ${AG_DUMP_MONTH_AGO_FILE} | ${PSQL} -d ${DEV_AG_DBNAME_TEST}"
${ZCAT} ${AG_DUMP_MONTH_AGO_FILE} | ${PSQL} -d ${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
RETVAL=$?
[ $RETVAL -ne 0 ] && exit $RETVAL

AG_UPDATE_FUNCTION_FILE=${AG_HOME}/ag1/db_backup/update_function.txt
logs "${PSQL} -d ${DEV_AG_DBNAME_TEST} -f ${AG_UPDATE_FUNCTION_FILE}"
${PSQL} -d ${DEV_AG_DBNAME_TEST} -f ${AG_UPDATE_FUNCTION_FILE} 1>>${LOGFILE} 2>&1
RETVAL=$?
[ $RETVAL -ne 0 ] && exit $RETVAL
#COMMENTOUT

#バックアップを元に環境を構築
makedata(){
	local CB_ID=$1
	local AG_CB_ID=$2
	local AG_DATASET_NAME=$3
	local TRIO_FILE=$4
	local LOGFILE="${DIRNAME}/logs/${BASENAME}.${DATE}.${CB_ID}.txt"
	local JSONFILE="${DIRNAME}/logs/${BASENAME}.${DATE}.${CB_ID}.json"
	local WORK_DBNAME=${DEV_DBNAME}_${DATE}_${CB_ID}

	echo "" 1>${LOGFILE} 2>&1
	logs "${CB_ID}"
	logs "${TRIO_FILE}"
	logs "${DB_NAME}"
	logs "${WORK_DBNAME}"

	SQL="DROP DATABASE IF EXISTS ${WORK_DBNAME}"
	logs "${SQL}"
	${PSQL} -c "${SQL}" 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	SQL="CREATE DATABASE ${WORK_DBNAME}"
	logs "${SQL}"
	${PSQL} -c "${SQL}" 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	#logs "${PSQL} -d ${WORK_DBNAME} -f ${PGHOME}/share/pgsenna2.sql"
	#${PSQL} -d ${WORK_DBNAME} -f ${PGHOME}/share/pgsenna2.sql 1>>${LOGFILE} 2>&1
	#RETVAL=$?
	#[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "${ZCAT} ${BACKUP_FILE} | ${PSQL} -d ${WORK_DBNAME}"
	${ZCAT} ${BACKUP_FILE} | ${PSQL} -d ${WORK_DBNAME} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	SQL="UPDATE model_version SET cb_id=${CB_ID}"
	logs "${SQL}"
	${PSQL} -d ${WORK_DBNAME} -c "${SQL}" 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "batch-recreate-subclass.pl"
	${NICE} ${WORK_HOME}/batch/batch-recreate-subclass.pl --database=${WORK_DBNAME} --ci_id=1 --cb_id=24 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	${NICE} ${WORK_HOME}/batch/batch-recreate-subclass.pl --database=${WORK_DBNAME} --ci_id=1 --cb_id=25 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "current_judgment_201903xx.pl"
	cd ${WORK_HOME}/201903xx/database/201903xx
	${NICE} ./current_judgment_201903xx.pl --db=${WORK_DBNAME} --cb=${CB_ID} --crl=0 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "${PSQL} -d ${WORK_DBNAME} -f ${WORK_HOME}/201903xx/database/201903xx/sql_201903xx.txt"
	${PSQL} -d ${WORK_DBNAME} -f ${WORK_HOME}/201903xx/database/201903xx/sql_201903xx.txt 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "batch-clear-subclass-tree-old.pl"
	cd ${WORK_HOME}/201903xx/batch
	${NICE} ./batch-clear-subclass-tree-old.pl --db=${WORK_DBNAME} --ci_id=1 --cb_id=${CB_ID} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "update_201903xx.pl"
	cd ${WORK_HOME}/201903xx/database/201903xx
	${NICE} ./update_201903xx.pl --db=${WORK_DBNAME} --port=${PGPORT} ${TRIO_FILE} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "batch-recreate-subclass.pl"
	cd ${WORK_HOME}/201903xx/batch
	${NICE} ./batch-recreate-subclass.pl --db=${WORK_DBNAME} --ci_id=1 --cb_id=${CB_ID} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "batch-create-freeze-mapping.pl"
	CUR_DATE=`date +'%Y-%m-%d %H:%M:%S'`
	JSON='{"cb_id":'${CB_ID}',"ci_id":1,"cmd":"create","crl_id":0,"datas":"[{\"fm_id\":0,\"fm_point\":false,\"fm_timestamp\":\"'${CUR_DATE}'\",\"fm_comment\":null,\"fm_status\":null}]","md_id":1,"mv_id":1}'
	echo ${JSON} > ${JSONFILE}
	logs "${WORK_HOME}/201903xx/batch/batch-create-freeze-mapping.pl --db=${WORK_DBNAME} --file=${JSONFILE}"
	${NICE} ${WORK_HOME}/201903xx/batch/batch-create-freeze-mapping.pl --db=${WORK_DBNAME} --file=${JSONFILE} 1>>${LOGFILE} 2>&1
	#logs "${WORK_HOME}/201903xx/batch/batch-create-freeze-mapping.pl --db=${WORK_DBNAME}"
	#${NICE} ${WORK_HOME}/201903xx/batch/batch-create-freeze-mapping.pl --db=${WORK_DBNAME} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	[ -f ${JSONFILE} ] && rm -fr ${JSONFILE}

	FREEZEFILE=${WORK_HOME}/201903xx/freeze_mapping/freeze_mapping_${CUR_DATE//[^0-9]/}.zip
	logs "${FREEZEFILE}"
	if [ -f ${BACKUP_FILE} -a -s ${BACKUP_FILE} ]; then
		FREEZEFILE_TIME=`date '+%Y/%m/%d %H:%M:%S' -r ${FREEZEFILE}`
		FREEZEFILE_EPOCHTIME=`date '+%s' -r ${FREEZEFILE}`
		FREEZEFILE_SIZE=`stat -c %s ${FREEZEFILE}`

		logs "${FREEZEFILE_TIME}"
		logs "${FREEZEFILE_EPOCHTIME}"
		logs "${FREEZEFILE_SIZE}"

		RAW_MAX_MV_ID=`${PSQL} -d ${DEV_AG_DBNAME_TEST} -x -t -A -c "SELECT MAX(mv_id) FROM model_version WHERE md_id=1"`
		logs "RAW_MAX_MV_ID=[${RAW_MAX_MV_ID}]"
		MV_ID=${RAW_MAX_MV_ID#max|}
		logs "MV_ID=[${MV_ID}]"
		MV_ID=$((MV_ID + 1))
		logs "MV_ID=[${MV_ID}]"

		logs "${AG_HOME}/BackStageEditor/201903xx/batch/batch-create-dataset.pl --db=${DEV_AG_DBNAME_TEST} --mv=${MV_ID} --cb=${AG_CB_ID} --name=${DATE}${AG_DATASET_NAME} --objectset=${DATE} --file=${FREEZEFILE}"
		cd ${AG_HOME}/BackStageEditor/201903xx/batch
		${NICE} ./batch-create-dataset.pl --db=${DEV_AG_DBNAME_TEST} --mv=${MV_ID} --cb=${AG_CB_ID} --name=${DATE}${AG_DATASET_NAME} --objectset=${DATE} --file=${FREEZEFILE} 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		SQL="DELETE FROM voxel_data WHERE art_hist_serial<>0"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		SQL="ALTER TABLE concept_art_map DISABLE TRIGGER trig_after_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE concept_art_map DISABLE TRIGGER trig_before_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="UPDATE concept_art_map SET art_hist_serial=0 WHERE art_hist_serial<>0"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE concept_art_map ENABLE TRIGGER trig_after_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE concept_art_map ENABLE TRIGGER trig_before_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		SQL="ALTER TABLE history_concept_art_map DISABLE TRIGGER trig_after_history_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE history_concept_art_map DISABLE TRIGGER trig_before_history_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="UPDATE history_concept_art_map SET art_hist_serial=0 WHERE art_hist_serial<>0"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE history_concept_art_map ENABLE TRIGGER trig_after_history_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE history_concept_art_map ENABLE TRIGGER trig_before_history_concept_art_map"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		SQL="ALTER TABLE history_art_file DISABLE TRIGGER trig_after_history_art_file"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE history_art_file DISABLE TRIGGER trig_before_history_art_file"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="DELETE FROM history_art_file WHERE hist_serial<>0"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE history_art_file ENABLE TRIGGER trig_after_history_art_file"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
		SQL="ALTER TABLE history_art_file ENABLE TRIGGER trig_before_history_art_file"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		SQL="UPDATE model_version SET mv_frozen=true,mv_modified=now() WHERE md_id=1 AND mv_id=${MV_ID}"
		logs "${SQL}"
		${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
	fi
}

if [ -f ${BACKUP_FILE} -a -s ${BACKUP_FILE} ]; then
	for ((i=0; i < ${CB_ID_SIZE}; i++)); do

		makedata ${CB_IDS[i]} ${AG_CB_IDS[i]} ${AG_DATASET_NAMES[i]} ${TRIO_FILES[i]}

	done

	logs "${AG_HOME}/BackStageEditor/201903xx/batch/make_art_to_voxel.pl --db=${DEV_AG_DBNAME_TEST}"
	cd ${AG_HOME}/BackStageEditor/201903xx/batch
	${NICE} ./make_art_to_voxel.pl --db=${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	sigint2 () {
		logs "trap INT or TERM"
		[ -f ${AG_DUMP_FILE} ] && rm -fr ${AG_DUMP_FILE}
	}

	logs "${PG_DUMP} ${DEV_AG_DBNAME_TEST} | ${GZIP} > ${AG_DUMP_FILE}"
	trap sigint2 INT TERM
	${PG_DUMP} ${DEV_AG_DBNAME_TEST} | ${GZIP} > ${AG_DUMP_FILE}
	RETVAL=$?
	if [ $RETVAL -ne 0 ]; then
		[ -f ${AG_DUMP_FILE} ] && rm -fr ${AG_DUMP_FILE}
		exit $RETVAL
	fi
	chmod 0400 ${AG_DUMP_FILE}
	trap '' INT TERM

	if [ -f ${AG_DUMP_FILE} ]; then
		chmod 0400 ${AG_DUMP_FILE}
		ln -s ${AG_DUMP_FILE} ${AG_DUMP_SUMLINK}
	fi

	SQL="DROP DATABASE IF EXISTS ${DEV_AG_DBNAME_TEST}"
	logs "${SQL}"
	${PSQL} -c "${SQL}" 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	SQL="CREATE DATABASE ${DEV_AG_DBNAME_TEST}"
	logs "${SQL}"
	${PSQL} -c "${SQL}" 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	logs "${ZCAT} ${AG_DUMP_FILE} | ${PSQL} -d ${DEV_AG_DBNAME_TEST}"
	${ZCAT} ${AG_DUMP_FILE} | ${PSQL} -d ${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

	SQL="ANALYZE VERBOSE"
	logs "${SQL}"
	${PSQL} -d ${DEV_AG_DBNAME_TEST} -c "${SQL}" 1>>${LOGFILE} 2>&1
	RETVAL=$?
	[ $RETVAL -ne 0 ] && exit $RETVAL

#<< COMMENTOUT

	if [ ! -d ${NEW_FMASEARCH_HOME} ]; then
		logs "${RSYNC} ${OLD_HOME}/ ${NEW_HOME}"
		${RSYNC} ${OLD_FMASEARCH_HOME}/ ${NEW_FMASEARCH_HOME} 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL
	fi

	if [ -d ${NEW_FMASEARCH_HOME} ]; then
		cd ${NEW_FMASEARCH_HOME}/htdocs_tools_xxx
		logs "./01_MENU_SEGMENTS_in_art_file.pl --db=${DEV_AG_DBNAME_TEST}"
		${NICE} ./01_MENU_SEGMENTS_in_art_file.pl --db=${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "./02_make_renderer_file.pl --db=${DEV_AG_DBNAME_TEST}"
		${NICE} ./02_make_renderer_file.pl --db=${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "./03_MENU_SEGMENTS_pointInsideObject.pl --db=${DEV_AG_DBNAME_TEST}"
		${NICE} ./03_MENU_SEGMENTS_pointInsideObject.pl --db=${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "./04_make_versions_file.pl --db=${DEV_AG_DBNAME_TEST}"
		${NICE} ./04_make_versions_file.pl --db=${DEV_AG_DBNAME_TEST} 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "find art_file/ -name \"*.obj\" | xargs ${NICE} ./zopfli.pl"
		find art_file/ -name "*.obj" | xargs ${NICE} ./zopfli.pl 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "find ../htdocs/renderer_file/renderer_file/ -name \"*.json\" | xargs ${NICE} ./zopfli.pl"
		find ../htdocs/renderer_file/renderer_file/ -name "*.json" | xargs ${NICE} ./zopfli.pl 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "find ../htdocs/MENU_SEGMENTS/ -name \"*.obj\" | xargs ${NICE} ./zopfli.pl"
		find ../htdocs/MENU_SEGMENTS/ -name "*.json" | xargs ${NICE} ./zopfli.pl 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "find ../htdocs/MENU_SEGMENTS/ -name \"*.json\" | xargs ${NICE} ./zopfli.pl"
		find ../htdocs/MENU_SEGMENTS/ -name "*.json" | xargs ${NICE} ./zopfli.pl 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "${NICE} ./zopfli.pl ../htdocs/renderer_file/art_file_info.json"
		${NICE} ./zopfli.pl ../htdocs/renderer_file/art_file_info.json 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

		logs "${NICE} ./zopfli.pl ../htdocs/renderer_file/versions_file.json"
		${NICE} ./zopfli.pl ../htdocs/renderer_file/versions_file.json 1>>${LOGFILE} 2>&1
		RETVAL=$?
		[ $RETVAL -ne 0 ] && exit $RETVAL

	fi
#COMMENTOUT

fi


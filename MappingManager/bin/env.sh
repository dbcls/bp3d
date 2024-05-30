#!/bin/bash
AG_HOME="/opt/services/ag"
AG_NUM="MappingManager"
#PGHOME="$AG_HOME/local/pgsql"
PGHOME="$AG_HOME/local"
PGBIN="$PGHOME/bin"
LD_LIBRARY_PATH="$PGHOME/lib"
PGDATA="$AG_HOME/$AG_NUM/pgdata"
PGPORT="38300"
PGUSER="postgres"
DBNAME="currentset_160614"
NEW_DBNAME="currentset_1903xx"
DEV_DBNAME="currentset_development"

AG_DBNAME="ag_public_1903xx"
AG_DBNAME_TEST="ag_public_1903xx_test"

LD_LIBRARY_PATH=/opt/services/ag/local/lib:/usr/local/lib/:/usr/lib
PYTHONPATH=/opt/services/ag/local/lib/python3.10/site-packages
PERL5LIB=/opt/services/ag/ag-test/htdocs:/opt/services/ag/ag-test/htdocs/API:/opt/services/ag/ag-test/htdocs/API/lib:/opt/services/ag/ag-test/lib:/opt/services/ag/ag-common/lib:/opt/services/ag/local/lib/perl5
PATH=/opt/services/ag/local/perl/bin:/opt/services/ag/local/bin:/opt/services/ag/local/apache/bin:/opt/services/ag/local/zopfli:/usr/local/bin:/usr/local/bin:/usr/local/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/ag/bin

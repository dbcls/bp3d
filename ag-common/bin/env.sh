#!/bin/bash
AG_HOME="/bp3d"
AG_NUM="ag-common"
PGSQL="$AG_HOME/local/pgsql"
LD_LIBRARY_PATH="$PGSQL/lib"
PGDATA="$AG_HOME/$AG_NUM/pgdata"
PORT="8543"
PGUSER="postgres"
DBNAME="bp3d_common"
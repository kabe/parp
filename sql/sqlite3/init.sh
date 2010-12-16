#!/bin/sh

DB_FILE=$1
SQLITE3="sqlite3 $DB_FILE"

if [ x = x"$DB_FILE" ];then
    echo Usage: $0 DB_FILE
    exit 1
fi

# Flee existing file
if [ -f $DB_FILE ]; then
    echo mv $DB_FILE $DB_FILE.`date +%Y%m%d-%H%M%S`
    mv $DB_FILE $DB_FILE.`date +%Y%m%d-%H%M%S`
fi
touch $DB_FILE

# Tables
echo CREATING TABLE PROFGROUP
$SQLITE3 < create_profgroup.sql
echo CREATING TABLE FUNCMAP
$SQLITE3 < create_funcmap.sql

echo CREATING TABLE PROFEXEC
$SQLITE3 < create_profexec.sql

echo CREATING TABLE PROFILE
$SQLITE3 < create_profile.sql
echo CREATING TABLE USEREVENT
$SQLITE3 < create_userevent.sql

# Views
echo CREATING VIEW MPIFUNC
$SQLITE3 < create_view_mpifunc.sql
echo CREATING VIEW FUNCPROFILE
$SQLITE3 < create_view_funcprofile.sql
echo CREATING VIEW FUNCRANKSUM
$SQLITE3 < create_view_funcranksum.sql
echo CREATING VIEW GROUPEXECMERGE
$SQLITE3 < create_view_groupexecmerge.sql

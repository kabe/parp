#!/bin/sh

if [ -z $DBUSER ]; then
    DBUSER=root
fi
if [ -z $DBNAME ]; then
    DBNAME=testparpdb
fi

echo Connect to database \'$DBNAME\' as user \'$DBUSER\'

echo 'DELETE FROM workflow; DELETE FROM workflow_trial;' | mysql -u $DBUSER $DBNAME


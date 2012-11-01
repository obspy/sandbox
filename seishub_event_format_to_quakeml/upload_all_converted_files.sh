#!/bin/bash
cd converted_files || exit 1
for FILE in *
do
    FILENAME=`echo $FILE | sed 's#\.xml$##'`.xml
    curl -v --data-binary @${FILE} -u admin:admin -X POST http://localhost:8080/xml/seismology/event/${FILENAME}
done

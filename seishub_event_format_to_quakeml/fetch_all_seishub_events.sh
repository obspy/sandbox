#!/bin/sh
mkdir -p all_resources
for FILE in `cat all_resource_names`
do
    if [ ! -f "all_resources/$FILE" ]
    then
        break
    fi
    wget -O all_resources/$FILE http://teide.geophysik.uni-muenchen.de:8080/xml/seismology/event/$FILE
done

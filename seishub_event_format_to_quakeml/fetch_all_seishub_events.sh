#!/bin/sh
mkdir all_resources
for FILE in `cat all_resource_names`
do
    wget -O all_resources/$FILE http://teide.geophysik.uni-muenchen.de:8080/xml/seismology/event/$FILE
done

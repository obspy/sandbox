#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Converts all StationXML files to SEED files.

folder="SEED/"
extension=".seed"
converter="~/Downloads/stationxml-converter-1.0.1.jar"

for i in StationXML/*.xml
    do
        name=`echo $i | cut -d'/' -f2`

        filename=$(basename "$name")
        filename="${filename%.*}"

        name=$folder$filename$extension

        if [ ! -f $name ]
        then
            echo "Converting " $i
            java -jar $converter -s $i > $name
        fi

    done

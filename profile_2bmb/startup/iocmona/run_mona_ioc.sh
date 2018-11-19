#!/bin/bash

# file: run_mona_ioc.sh
# purpose: provide PVs for MONA modules to advise BlueSky

#softIoc -d ./mona.db

# run in screen session: 
/usr/bin/screen -dm -S mona -h 5000 softIoc -d ./mona.db

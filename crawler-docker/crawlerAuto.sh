#!/bin/bash

#  set Path
pydata= /home/iii/Desktop/py_data
pydir= /home/iii/Desktop/py_dir

# Start running

echo '==move url database=='
test -f $pydata/mobile01_history.json && mv $pydata/mobile01_history.json $pydir
test -f $pydata/pixnet_url_database.json && mv $pydata/pixnet_url_database.json $pydir
echo '==check dir=='
test -d  $pydata || mkdir $pydata
echo '==build image=='
docker build -t py/image $pydir
echo '==run container=='
docker run -dt --name py_container -v $pydir:/py_dir py/image ping localhost
echo '==exec py=='
docker exec py_container python /py_dir/pixnet_tourist_latest_hot.py
docker exec py_container python /py_dir/pixnet_tourist_new.py
docker exec py_container python /py_dir/mobile01_tourist.py
echo '==mv file=='
mv $pydir/*.json $pydata
echo '==rm container & image=='
docker rm -f py_container
docker rmi -f py/image
echo '==done=='

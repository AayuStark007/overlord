#! /bin/bash

pushd $1
git pull origin master
source ./env/bin/activate
python client.py --ip aayushgupta.dev --use_pi -x 640 -y 480
popd

#! /bin/bash

cd /vagrant
sudo python setup.py install
#roger deploy roger-simple ma.yml -e local
roger deploy roger-simpleapp roger.yml -e local

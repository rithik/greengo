#!/bin/bash

python3 greengo.py --config_file=Group-0.yaml --bulk True remove
rm -r Group-0.yaml Group-0-GG-Config/ certs.tar.gz

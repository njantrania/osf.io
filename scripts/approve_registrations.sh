#!/bin/bash

export HOME="/home"
cd /opt/apps/osf
source env/bin/activate
python -m scripts.approve_registrations

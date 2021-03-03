#!/usr/bin/bash

CURRENT_DIR=$(pwd)

cd ../ansible || exit

ansible-playbook -i inventory -u terra grafana.yml

cd "$CURRENT_DIR" || return

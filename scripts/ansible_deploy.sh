#!/usr/bin/bash

CURRENT_DIR=$(pwd)

cd ../ansible || exit

ansible-playbook -i inventory -u terra nfs.yml

nfs=$?
if [ -$nfs -eq 0 ]; then
  ansible-playbook -i inventory -u terra kubernetes.yml
fi

kubernetes=$?
if [ -$kubernetes -eq 0 ]; then
  ansible-playbook -i inventory -u terra master.yml
fi

master=$?
if [ -$master -eq 0 ]; then
  ansible-playbook -i inventory -u terra workers.yml
fi

cd "$CURRENT_DIR" || return
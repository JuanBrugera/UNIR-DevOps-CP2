#!/usr/bin/bash

CURRENT_DIR=$(pwd)

terraform destroy -auto-approve

cd "$CURRENT_DIR" || return

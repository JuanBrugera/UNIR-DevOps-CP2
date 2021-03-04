#!/usr/bin/python

import os
import re
import shutil
import subprocess
import sys
import time

from datetime import datetime, timedelta
from typing import Callable
from pathlib import Path


def parent_path(path: str, level: int = 1) -> str:
    """This method, given a path, return its level parent folder"""
    parent = os.path.split(path)[0]
    if level == 1:
        return parent
    else:
        return parent_path(parent, level - 1)


# path constants
HOME = Path.home()
SSH_PATH = os.path.join(HOME, '.ssh')
BOOTSTRAP_PATH = os.path.abspath(__file__)
PROJECT_PATH = parent_path(BOOTSTRAP_PATH, 2)
SCRIPTS_PATH = os.path.join(PROJECT_PATH, 'scripts')
ANSIBLE_PATH = os.path.join(PROJECT_PATH, 'ansible')

# regex to find token and discovery from master playbook
TOKEN_REGEX = re.compile(r'--token (\w{6}\.\w{16})')
DISCOVERY = re.compile(r'--discovery-token-ca-cert-hash (sha256:\w{64})')

# time to wait before ansible playbooks
WAIT_MINUTES = 3

# lambda to check if a file is a shell script
is_sh: Callable[[str], bool] = lambda file: file.endswith('.sh')

if __name__ == '__main__':
    try:
        begin_at = int(sys.argv[1])
    except IndexError:
        begin_at = 0

    options = {'0': 'apply and deploy', '1': 'destroy'}
    for k, v in options.items():
        print("{}: {}".format(k, v))
    option = input("Please select an option: ")

    # list scripts folder a filter sh files in order
    sh_files = list(sorted(filter(is_sh, os.listdir(SCRIPTS_PATH))))

    for sh_file in sh_files[begin_at:]:
        # option = 0 is for apply and deploy. option = 1 is for destroy
        if sh_file.startswith(option):
            # absolute path to sh file
            sh_file_path = os.path.join(SCRIPTS_PATH, sh_file)
            # -rwxr--r-- permissions
            os.chmod(sh_file_path, 0o744)
            # retrieving token and discovery from master playbook output
            if "ansible_master" in sh_file:
                output = subprocess.check_output([sh_file_path]).decode()
                token = TOKEN_REGEX.search(output)
                discovery = DISCOVERY.search(output)
                if (token is None) or (discovery is None):
                    print(token, discovery, output)
                    raise ValueError("Token or Discovery not found")
                else:
                    token_value = token.group(1)
                    discovery_value = discovery.group(1)
                    # if found, generate new workers.yml from template
                    with open(os.path.join(ANSIBLE_PATH, 'workers.yml.template'), 'r') as source:
                        data = source.read()
                        with open(os.path.join(ANSIBLE_PATH, 'workers.yml'), 'w') as destination:
                            destination.write(
                                data.replace("@DISCOVERY@", discovery_value).replace("@TOKEN@", token_value))
                            destination.close()
                        source.close()
            # copying ssh config file to $HOME/.ssh
            elif "ansible" in sh_file:
                shutil.copy(
                    os.path.join(PROJECT_PATH, 'files', '.ssh', 'config'),
                    os.path.join(SSH_PATH, 'config')
                )
                subprocess.call([sh_file_path])
            # waiting for virtual machines 100% operative
            else:
                status = subprocess.check_call([sh_file_path])
                if ("terraform_apply" in sh_file) and (status == 0):
                    print(f"Waiting {WAIT_MINUTES} minutes for VMs 100% working...")
                    print(f"Execution will continue @ {datetime.now() + timedelta(minutes=WAIT_MINUTES)}")
                    time.sleep(WAIT_MINUTES * 60)

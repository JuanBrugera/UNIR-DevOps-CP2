#!/usr/bin/python

import os
import shutil
import subprocess
import time

from datetime import datetime, timedelta
from typing import Callable
from pathlib import Path

HOME = Path.home()
SSH_PATH = os.path.join(HOME, '.ssh')
USER = 'terra'
PASSWORD = '@._admin4dm1n$'
VIRTUAL_MACHINES = [
    "nfs-jbrug91.westeurope.cloudapp.azure.com",
    "k8smaster-jbrug91.westeurope.cloudapp.azure.com",
    "k8sworker0-jbrug91.westeurope.cloudapp.azure.com",
    "k8sworker1-jbrug91.westeurope.cloudapp.azure.com",
]

is_sh: Callable[[str], bool] = lambda file: file.endswith('.sh')


def parent_path(path: str, level: int = 1) -> str:
    parent = os.path.split(path)[0]
    if level == 1:
        return parent
    else:
        return parent_path(parent, level - 1)


def ssh_copy_id(vm: str):
    id_rsa_pub = os.path.join(SSH_PATH, 'id_rsa.pub')
    args = ["ssh-copy-id", "-i", id_rsa_pub, f"{USER}@{vm}"]
    proc = subprocess.Popen(args,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    time.sleep(0.2)
    proc.stdin.write('yes\n')
    time.sleep(0.2)
    proc.stdin.write(f'{PASSWORD}\n')
    proc.stdin.flush()
    stdout, stderr = proc.communicate()
    print(stdout)
    print(stderr)


if __name__ == '__main__':
    options = {'0': 'apply and deploy', '1': 'destroy'}
    for k, v in options.items():
        print("{}: {}".format(k, v))
    option = input("Please select an option: ")

    bootstrap_path = os.path.abspath(__file__)
    project_path = parent_path(bootstrap_path, 2)

    scripts_path = os.path.join(project_path, 'scripts')
    sh_files = list(sorted(filter(is_sh, os.listdir(scripts_path))))

    for sh_file in sh_files:
        if sh_file.startswith(option):
            sh_file_path = os.path.join(scripts_path, sh_file)
            # add rwxr--r-- permissions to sh files
            os.chmod(sh_file_path, 0o744)
            if "ansible_master" in sh_file:
                output = subprocess.check_output([sh_file_path]).decode()
            else:
                status = subprocess.check_call([sh_file_path])
                if ("terraform_apply" in sh_file) and (status == 0):
                    minutes = 5
                    print(f"Waiting {minutes} minutes for DNS refreshing...")
                    print(f"Execution will continue @ {datetime.now() + timedelta(minutes=minutes)}")
                    time.sleep(minutes * 60)
                    os.remove(os.path.join(SSH_PATH, 'known_hosts'))
                    for virtual_machine in VIRTUAL_MACHINES:
                        ssh_copy_id(virtual_machine)

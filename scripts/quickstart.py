#!/usr/bin/python

import os
import subprocess

from typing import Callable

is_sh: Callable[[str], bool] = lambda file: file.endswith('.sh')


def parent_path(path: str, level: int = 1) -> str:
    parent = os.path.split(path)[0]
    if level == 1:
        return parent
    else:
        return parent_path(parent, level - 1)


if __name__ == '__main__':
    options = {'0': 'apply and deploy', '1': 'destroy'}
    for k, v in options.items():
        print("{}: {}".format(k, v))
    option = input("Please select an option: ")
    bootstrap_path = os.path.abspath(__file__)
    project_path = parent_path(bootstrap_path, 2)
    scripts_path = os.path.join(project_path, 'scripts')
    sh_files = list(sorted(filter(is_sh, os.listdir(scripts_path))))

    # add rwxr--r-- permissions to sh files
    for sh_file in sh_files:
        if sh_file.startswith(option):
            sh_file_path = os.path.join(scripts_path, sh_file)
            os.chmod(sh_file_path, 0o744)
            subprocess.call([sh_file_path])

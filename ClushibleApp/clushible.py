#!/usr/bin/env python3.12

# Load Modules
import os
import sys
import random
import time
import io
import math

import threading
from concurrent.futures.thread import ThreadPoolExecutor

from pathlib import Path

from ClusterShell.NodeSet import NodeSet,expand
from ClusterShell.Task import Task, task_self


# Load Local Modules
from ClushibleApp import config
from ClushibleApp.utils import msg
from ClushibleApp.utils.ansible import validate_ansible_setup, generate_playbook_cmd


def show_config(args:dict):
    msg.info("Configuration")
    sys.stdout.write("====================\n")
    for section,opts in vars(args).items():
        print(f"{section}:")
        for key,val in vars(opts).items():
            print(f"  {key}: {val}")
    sys.stdout.write("====================\n\n")

def main():

    conf = config.get_config()

    # Set some silly defaults if not set
    if conf.ansible.forks == ""  or conf.ansible.forks is None:
        conf.ansible.forks = 25
    
    if conf.core.verbose > 0:
        show_config(conf)

    runners = NodeSet(conf.clushible.runners)
    targets = NodeSet(conf.clushible.target)

    if len(runners) == 0:
        msg.warn("No runners specified, defaulting to localhost.")
        runners = NodeSet("localhost")

    if len(targets) == 0:
        msg.error("No targets specified, exiting.")
    # Validate Ansible Paths Locally
    validate_ansible_setup(conf)


    # Get the runners
    nproc = "/usr/bin/nproc"
    if os.uname().sysname == "Darwin":
        nproc = "/usr/bin/sysctl -n hw.ncpu"

    # Assume count of runners is good for now
    subtargets = [x for x in targets.split(len(runners))]

    print(f"Number of subtargets: {len(subtargets)}")
    for s in subtargets:
        print(f"subtarget: {s}")



    # Data Deployment
    # TODO

    # Generate Ansible Playbook Commands
    playbook_cmd = generate_playbook_cmd(conf, targets)

    # Execution

    
    # Data Gather
    
    # Error Reports
    
    # Exit / Complete


if __name__ == "__main__": main()

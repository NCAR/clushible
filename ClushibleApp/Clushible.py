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
from ClushibleApp.utils.dispatch import get_runner_procs,run

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
    #if conf.ansible.forks == 0  or conf.ansible.forks is None:
    #    conf.ansible.forks = 25
    
    if conf.core.verbose > 2:
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
    FORCED_NSETS=False
    if conf.clushible.sets == 0:
        conf.clushible.sets = len(runners)
    else:
        FORCED_NSETS=True

    if conf.clushible.sets > len(targets):
        msg.warn("nsets greater than len(targets), shrinking nsets to len(targets).")
        conf.clushible.sets = len(targets)

    # Return a dictionary of nproc (or equivalent) processor count on the runners
    rprocs = get_runner_procs(conf, runners)

    if conf.ansible.forks == 0 and conf.core.verbose > 0:
        conf.ansible.forks = int(conf.clushible.fscale * max(rprocs.values()))
        msg.info(f"Forks is auto-detected. Setting to {conf.ansible.forks}")

    # MAGIC
    subtargets = []
    if len(targets)/conf.clushible.sets > (conf.clushible.fscale*max(rprocs.values())):
        if FORCED_NSETS:
            msg.warn("nsets specified as non-zero, but greater than recommended forks, expect slow down.")
        else:
            conf.clushible.sets = math.ceil(len(targets) / (conf.clushible.fscale*max(rprocs.values())))
            if conf.core.verbose > 0:
                msg.info(f"Setting nsets with groups of ~{conf.clushible.fscale}*{max(rprocs.values())} for '{conf.clushible.distribution}' distribution.")

    if conf.clushible.distribution == 'pack':
        tgt = list(targets)
        for i in range(0, len(targets), conf.ansible.forks):
            subtargets.append(NodeSet.fromlist(tgt[i:i+conf.ansible.forks]))
    else:
        # if conf.clushible.distribution == 'scatter'
        subtargets = [x for x in targets.split(conf.clushible.sets)] 
        
    #subtargets = [x for x in targets.split(conf.clushible.sets)]

    if conf.core.verbose > 0:
        print(f"Number of subtargets sets: {len(subtargets)}")
        for s in subtargets:
            print(f"subtarget: {s} ({len(s)})")

    if conf.core.partition_only: sys.exit(0)
    # Data Deployment
    # TODO

    # Generate Ansible Playbook Commands
    playbook_cmd = [generate_playbook_cmd(conf, t) for t in subtargets]

    # dummy command list for testing
    #cmd_list = [f"echo 'hello {i}'" for i in range(100)]


    results = run(conf, playbook_cmd)
    print(results)
    sys.exit(0)

    print(f"\nStatus:")
    for s in status:
        try: 
            print(str(s.decode('utf-8')))
            print()
        except AttributeError:
            print(str(s))
            print()
            

    
    # Data Gather
    
    # Error Reports
    
    # Exit / Complete


if __name__ == "__main__": main()

#!/usr/bin/env python3.12
import os

import threading
from concurrent.futures.thread import ThreadPoolExecutor

from Clustershell.NodeSet import NodeSet
from Clustershell.Task import Task, task_self

from . import msg

def get_runner_procs(conf, runners):
    nproc_cmd = "/usr/bin/nproc"
    if os.uname().sysname == "Darwin":
        nproc_cmd = "/usr/sbin/sysctl -n hw.ncpu"
    
    R = task_self()
    R.run(nproc_cmd, nodes=runners)
    for rc,nodelist in R.iter_retcodes():
        n = NodeSet.fromlist(nodelist)
        if conf.core.verbose > 0:
            msg.info(f"Runner Nodeset: {n}, nproc return code: {rc}")

        if rc != 0:
            runners.remove(n)
            msg.warn(f"Some runner nodes in {n} are not responding, excluding from runners.")




#def check_runners(conf, runners):
#    """Checks the availability of runner nodes."""
#    from ClusterShell.Task import Task, task_self
#    from ClushibleApp.utils import msg
#
#    nproc_cmd = "/usr/bin/nproc"
#    R = task_self()
#    R.run(nproc_cmd, nodes=runners)
#
#    alive_runners = NodeSet()
#    for n in R.nodes():
#        t = R.find_node(n)
#        if t.exitcode == 0:
#            alive_runners.add(n)
#        else:
#            msg.warn(f"Runner node {n} is not responding, excluding from runners.")
#
#    if len(alive_runners) == 0:
#        msg.error("No alive runner nodes available. Exiting.")
#
#    if conf.core.verbose > 0:
#        msg.info(f"Alive Runners: {','.join(expand(alive_runners))}")
#
#    return alive_runners

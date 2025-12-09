#!/usr/bin/env python3.12
import os
import time

import threading
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed

from ClusterShell.NodeSet import NodeSet
from ClusterShell.Task import Task, task_self

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
            msg.warn(f"Some runner are not responding or had a non-zero RC({rc}); excluding {n} from runners.")

    rprocs = {}
    for b,nodelist in R.iter_buffers(match_keys=runners):
        ns = NodeSet.fromlist(nodelist)
        out = int(b.message().decode("utf-8"))
        for n in nodelist: 
            rprocs[n] = out
        
    if conf.core.verbose > 0:
        msg.info(f"Max runner proc: {max(rprocs.values())}")
        msg.info(f"Min runner proc: {min(rprocs.values())}")
        if conf.core.verbose > 1:
            msg.info(f"Recommended forks = {4*min(rprocs.values())}")

    return rprocs

def run_task(conf, cmd, t2r:dict):
    th = threading.current_thread()
    thn = th.getName()
    thi = th.ident

    # Create ClusterShell Tasks w/ thread
    t = Task(th)

    #print(t2r)
    runner = t2r[thi]
    
    if conf.core.verbose > 0:
        print(f":: {runner}: {cmd}\n")
    #msg.info(f"{runner}({thn} {thi}): {cmd}")
    t.run(cmd,nodes=runner)
    t.join()
    return t.node_buffer(runner)
    #return t.max_retcode()

def check_thread():
    # ThreadPoolExecutgor creates lazy, make it force via sleep. FIX ME
    th = threading.current_thread()
    time.sleep(.2)

def run(conf, cmds:list):
    r_ns = NodeSet(conf.clushible.runners)

    grange = [i for i in range(len(r_ns))]
    thread_to_runner = dict()
    pool_size = len(r_ns)
    with ThreadPoolExecutor(max_workers=pool_size) as executor:
        main_th = threading.current_thread()
        #print(f"Main Thread: {main_th.ident}")
        ch = []
        for i in grange:
            ch.append( executor.submit(check_thread) )
        for r in as_completed(ch):
            r.result()
        
        #Create a map thread_to_runner[th.ident] = runner
        r_list = list(r_ns)
        for i in threading.enumerate():
            if main_th == i: continue
            thread_to_runner[i.ident] = r_list.pop(0)
            #print(thread_to_runner)

        #msg.info(f"{thread_to_runner}")

        rcs = []
        for c in cmds:
            rcs.append(executor.submit(run_task,conf,c,thread_to_runner))
        
        results = []
        for r in as_completed(rcs):
            results.append(r.result())

        #for r in results:
        #    print(r.decode('utf-8'))

    if conf.clushible.collate is True:
        return collate_results(conf,results)
    return results

# I think this will lose it's sorted order :/ maybe
def collate_results(conf,results):
    output_dict = dict()
    for r in results:
        data = r.decode('utf-8').split('\n')
        for line in data:
            if ':' not in line: continue

            node, info = line.split(':', 1)
            node = node.strip()
            info = info.strip()

            if info not in output_dict:
                output_dict[info] = []
            output_dict[info].append(node)
    
    #collapsed_common = dict()
    #for k,v in output_dict.items():
    #    print(f"{k} --> {v}")
    #    if v not in collapsed_common.values():
    #        collapsed_common[v] = []
    #    collapsed_common[v].append(k)
    #print(collapsed_common)

    coll_results = []
    for info, nodes in output_dict.items():
        nodeset = NodeSet.fromlist(nodes)

        if conf.clushible.coll_header:
            coll_results.append(f"{nodeset}: {info}")
        else:
            # Format with separator lines
            separator = "-" * 15
            coll_results.append(separator)
            coll_results.append(f"{nodeset} ({len(nodeset)})")
            coll_results.append(separator)
            coll_results.append(info)
            coll_results.append("")
        
    #print('\n'.join(coll_results))
    return '\n'.join(coll_results)


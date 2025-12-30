#!/usr/bin/env python3.12

# Load Modules
from pprint import pprint
import sys
import math

from ClusterShell.NodeSet import NodeSet

# Load Local Modules
from ClushibleApp import __version__
from ClushibleApp.config import CONFIG
from ClushibleApp.utils import msg
from ClushibleApp.utils.ansible import (
    validate_ansible_setup,
    generate_playbook_cmd,
)
from ClushibleApp.utils.dispatch import get_runner_procs, run


def show_config(args: dict) -> None:
    msg.info("Configuration")
    sys.stdout.write("====================\n")
    for section, opts in vars(args).items():
        print(f"{section}:")
        for key, val in vars(opts).items():
            print(f"  {key}: {val}")
    sys.stdout.write("====================\n\n")


def main() -> int:
    # Configuration is now a singleton (still namespace-based though)
    conf = CONFIG

    if conf.core.version:
        print(f"Clushible {__version__}")
        sys.exit(0)

    if conf.core.verbose > 2:
        show_config(conf)

    runners = NodeSet(conf.clushible.runners)
    targets = NodeSet(conf.clushible.targets)

    if len(runners) == 0:
        msg.warn("No runners specified, defaulting to localhost.")
        conf.clushible.runners = "localhost"
        runners = NodeSet(conf.clushible.runners)

    if len(targets) == 0:
        msg.error("No targets specified, exiting.")

    # Validate Nodesets
    if (
        conf.clushible.valid_targets is None
        and not conf.clushible.disable_target_validation
    ):
        conf.clushible.disable_target_validation = True
        msg.warn(
            "Configuration of valid_targets is not defined. Skipping target validation."
        )

    if not conf.clushible.disable_target_validation:
        invalid_targets = targets.difference(conf.clushible.valid_targets)
        if len(invalid_targets) > 0:
            msg.error(f"Invalid targets found: {invalid_targets}, exiting.")

    # Validate Ansible Paths Locally
    validate_ansible_setup(conf)

    # Return a dictionary of nproc (or equivalent) processor count on the runners
    rprocs = get_runner_procs(conf)

    # Reset runners based on testing usable runners
    runners = NodeSet(conf.clushible.runners)

    # Make sure fscale is set to non-zero
    if conf.clushible.fscale == 0:
        conf.clushible.fscale = 4  # Empirical default

    # Assume count of runners is good for now
    FORCED_NSETS = False
    if conf.clushible.nsets == 0:
        conf.clushible.nsets = len(runners)
    else:
        FORCED_NSETS = True

    if int(conf.clushible.nsets) > len(targets):
        msg.warn(
            "nsets greater than len(targets), shrinking nsets to len(targets)."
        )
        conf.clushible.nsets = len(targets)
    if conf.ansible.forks == 0:
        if conf.core.verbose > 0:
            msg.info(
                f"Forks is auto-detected. Setting to {int(conf.clushible.fscale * min(rprocs.values()))}"
            )
        conf.ansible.forks = int(conf.clushible.fscale * min(rprocs.values()))

    # MAGIC
    subtargets = []
    if len(targets) / conf.clushible.nsets > int(
        conf.clushible.fscale * min(rprocs.values())
    ):
        if FORCED_NSETS:
            msg.warn(
                "nsets specified as non-zero, but greater than recommended forks, expect slow down."
            )
        else:
            conf.clushible.nsets = math.ceil(
                len(targets) / (conf.clushible.fscale * min(rprocs.values()))
            )
            if conf.core.verbose > 0:
                msg.info(
                    f"Setting nsets with groups of ~{conf.clushible.fscale}*{min(rprocs.values())} for '{conf.clushible.distribution}' distribution."
                )

    if conf.clushible.distribution == "pack":
        tgt = list(targets)
        for i in range(0, len(targets), conf.ansible.forks):
            subtargets.append(
                NodeSet.fromlist(tgt[i : i + conf.ansible.forks])
            )
    else:
        # if conf.clushible.distribution == 'scatter'
        subtargets = [x for x in targets.split(conf.clushible.nsets)]

    if conf.core.verbose > 0:
        msg.info(f"Number of subtargets sets: {len(subtargets)}")
        for s in subtargets:
            msg.info(f"subtarget: {s} ({len(s)})")

    if conf.clushible.partition_only:
        return 0

    # Data Deployment (if !nfs, do some sort of VCS operation and place password
    # file in a proper spot. This might include doing some operations in a
    # location like /tmp or /var/tmp.)
    # TODO

    # Generate Ansible Playbook Commands
    playbook_cmd = [generate_playbook_cmd(conf, t) for t in subtargets]

    # Results collected and returned as large string as usually collated
    results = run(conf, playbook_cmd)
    print(results)

    # Data Gather
    # Gather Log as necessary.

    # Error Reports
    # Find any worrisome errors.

    # Do a final cleanup

    # Exit / Complete
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/opt/clmgr/python-310/bin/python3.10

import sys
import time
import argparse
import pathlib

import ClusterShell.NodeSet


parser = argparse.ArgumentParser(
        prog="clushible",
        description='Run Ansible on Runners through ClusterShell (clush)',
        epilog='Bugs can be reported here: https://github.com/ncar/clushible'
        )

parser.add_argument("--verbose", "-v",
                    action="count",
                    default=0,
                    help="verbose output"
                    )

parser.add_argument("--debug", "-d",
                    action="count",
                    default=0,
                    help="Debug information (on stderr)"
                    )

parser.add_argument("--config", "-c",
                    dest="config_file",
                    type=pathlib.Path,
                    nargs='?',
                    help="use alternative config to ./clushible.cfg"
                    )

parser.add_argument("--ansible-playbook-cmd", "-A",
                    type=pathlib.Path,
                    nargs='?',
                    default=pathlib.Path("/opt/ncar/ansible/bin/ansible-playbook"),
                    help="override the default ansible-playbook command"
                    )

parser.add_argument("--ansible-dir","-a",
                    type=pathlib.Path,
                    nargs='?',
                    default=pathlib.Path("/opt/ncar/hsg-ansible"),
                    help="path to ansible directory"
                    )

parser.add_argument("--limit", "-l",
                    dest="limit",
                    type=ClusterShell.NodeSet.NodeSet, 
                    nargs='?',
                    required=True,
                    help="the end nodes to limit the ansible runs to"
                   )

parser.add_argument("--runners", "-r",
                    dest="runners", 
                    type=ClusterShell.NodeSet.NodeSet,
                    nargs='?',
                    required=True,
                    help="the runners that can have work farmed out to"
                    )

parser.add_argument("--vault-password-file",
                    dest="vault_password_file",
                    type=pathlib.Path,
                    default=pathlib.Path("/root/ansible.passwd"),
                    nargs='?',
                    help="the ansible-vault password file that will be copied to runners"
                    )

parser.add_argument("--forks", "-f", 
                    dest="forks",
                    type=int, 
                    nargs='?',
                    default=36,
                    help="the number of forks to run per Ansible instance."
                    )

parser.add_argument("--inventory", "-i",
                    dest="inventory_file",
                    type=pathlib.Path, 
                    nargs='?',
                    required=True,
                    help="The inventory file to use."
                    )

parser.add_argument("--check",
                    dest="check",
                    action="store_true",
                    help="Whether to run in check mode (default = False )."
                    )

parser.add_argument("--log-method", "-L",
                    dest="log_method",
                    type=str,
                    nargs='?',
                    choices = ('segmented', 'collated', 'syslog'),
                    help="The logging method selected: syslog, segmented, collated."
                    )

parser.add_argument("--distribute", "-D",
                    type=str,
                    nargs='?',
                    choices=('pack', 'spread'),
                    default='spread',
                    help="Pack the runners or spread the load."
                    )

parser.add_argument("playbook",
                    type=pathlib.Path,
                    nargs='?',
                    default=pathlib.Path("/opt/ncar/hsg-ansible/nwsc3-playbook.yml"),
                    help="the playbook to be run on the runners to computes"
                    )

if __name__ == "__main__":
    parser.print_help()

# clushible
ClusterShell Wrapper for Ansible


## Basic Idea
Scale up Ansible runners by providing upper level controller that triggers other nodes to execute the Ansible playbooks.

The overall goal is to reduce the amount of Ansible runtime on NCAR's HPE CrayEX supercomputer which is about 2,500 servers.

This is really designed to blast a large number of Ansible playbooks to run in series of batches using 'runner' nodes.

## Requirements

Presently, Ansible and your Ansible directory should be on shared NFS or other type of filesystem. 

Right

## Examples

`clushible --ansible-dir="/path/to/ansible_directory" --runners @su-leader --inventory /path/to/ansible/inventory.yml --limit $TGT_NODES /path/to/ansible/playbook.yml`

In the above, `ansible-dir` is where your configuration is held. Anywhere node collections that can be implemented by ClusterShell can be used and they will be broken up and expanded in Ansible syntax on the `--limit` parameter. `--runners` is similar, but are the nodes that will run the ansible-playbook itself.

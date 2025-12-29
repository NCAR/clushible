# clushible

ClusterShell Wrapper for Ansible

## Basic Idea

Scale up Ansible runners by providing upper level controller that triggers other
\[service\] nodes to execute the Ansible playbooks as semi-independent
controllers for a subset of nodes at a time..

The overall goal is to reduce the amount of Ansible runtime on large quantities
of servers (>100) and where the primary Ansible controller may have minimal
resource requirements. It can be thought of somewhat a batching method to
service nodes that utilized ClusterShell configuration.

## Requirements

Presently, Ansible and your Ansible directory should be on shared NFS or other type of filesystem.

Python. Please try to use at least Python 3.8 or preferrably Python 3.11 or newer.

A Python virtual environment is a preferred method for installation. Basic
requirements for the installation are a TOML implementation (`tomli` or
`tomllib` (Python >= 3.11)) and ClusterShell. A `requirements.txt` file is
provided in this repository.

## Installation

### Install from git?

```sh
git clone https://github.com/ncar/clushible.git /path/to/clone

cd /path/to/clone

python3 -m venv /path/to/install

. /path/to/install/bin/activate

python3 -m pip install .
```

### Install direct from Github

```sh
python3 -m venv /path/to/install

.  /path/to/install/bin/activate

python3 -m pip install git+https://github.com/ncar/clushible.git
```

### Install from `requirements.txt`

```sh
python3 -m venv /path/to/install

. /path/to/install/bin/activate

python3 -m pip install -r <( curl https://raw.githubusercontent.com/NCAR/clushible/refs/heads/main/requirements.txt )
```

### Post Installation Tasks

Generally, I don't like to always have the virtual environment activated, but
this can be easily remediated with either a symbolic link or hard link depending
on your preference (symlink for me, but your security stance may differ)

At NCAR, we have `sudo` capability for engineers / operators for
`/opt/ncar/sbin`, so I generally drop a symlink in that directory and now my
team can use with easily.

I've also provided a sample role (warning, it's just copied from our operations
ansible; you'll need to read it).

## Configuration File

The configuration file is in TOML format. An [example](etc/clushible.toml) is
provided, but basically follows the syntax of `[section].[option]` from the
`--help` output. More options are being added to support more dynamic runs of
Ansible, but sensible defaults will be given as to not require
over-specification.

The most critical bits are to make sure that project directory, playbook, and
inventory is specified. I use flat inventories and not dynamic ones, so be aware
of that; it may change as we explore more hybrid cloud environments.

It's also a good idea to identify your ClusterShell configuration if you want to
specify it as not part of your virtual environment. You can use
`/etc/clustershell` as an option, but I actually prefer to be specific here as
often a vendor can get in my way and change various things.

## Examples

```sh
clushible -vvv -w $NODE_SET \
  --runners=$RUNNER_NODESET \
  --project-dir=/path/to/ansible/project \
  --inventory=/path/to/ansible/inventory.yml \
  --playbook=/path/to/ansible/playbook.yml \
  --ansible-vault-passwd-file /path/to/vault.passwd
```

```sh
clushible -w $NODE_SET --playbook /path/to/specific/playbook
```

```sh
clushible -w $NODE_SET
```

```sh
clushible -w $NS --tags=specific_tag
```

```sh
clushible -w $NS --check
```

```sh
clushible --dry-run -w $NS
```

## Personal Notes

Nothing yet ... TBD

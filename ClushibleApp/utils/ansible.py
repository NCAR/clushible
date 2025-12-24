#!/usr/bin/env python3.12

from pathlib import Path

from ClusterShell.NodeSet import NodeSet, expand

from . import msg


def validate_ansible_setup(conf):
    """Validates that Ansible paths exist on the local system."""
    if not Path(conf.ansible.playbook_cmd).exists():
        msg.error(
            f"Ansible path {conf.ansible.playbook_cmd} does not exist locally. Exiting."
        )

    if not Path(conf.ansible.project_dir).is_dir():
        msg.error(
            f"Ansible project dir {conf.ansible.project_dir} does not exist. Exiting."
        )

    if not Path(conf.ansible.inventory).exists():
        msg.error(
            f"Ansible inventory file {conf.ansible.inventory} does not exist. Exiting."
        )

    if not Path(conf.ansible.vault_passwd_file).exists():
        msg.error(
            f"Ansible vault password file {conf.ansible.vault_passwd_file} does not exist. Exiting."
        )


def generate_playbook_cmd(conf, target: NodeSet, extra_vars: dict = {}):
    """Generates the Ansible playbook command based on configuration and extra vars."""
    cmd = [
        f"cd {conf.ansible.project_dir}; ",
        "export ANSIBLE_STDOUT_CALLBACK=clushible; ",
        "/usr/bin/echo" if conf.core.dry_run else "",
        conf.ansible.playbook_cmd,
        f"-i {conf.ansible.inventory}",
        f"--forks {str(conf.ansible.forks)}",
        f"--vault-password-file {conf.ansible.vault_passwd_file}",
        "-C" if conf.ansible.check else "",
        f"-l {','.join(expand(target))}",  # ",".join(expand(target)),
        f"--tags={conf.ansible.tags}" if conf.ansible.tags else "",
        f"--skip-tags={conf.ansible.skip_tags}"
        if conf.ansible.skip_tags
        else "",
        str(conf.ansible.playbook),
    ]

    for k, v in extra_vars.items():
        cmd.extend(["--extra-vars", f"{k}={v}"])

    if conf.core.verbose > 1:
        msg.info(f"\nAnsible Playbook Command:\n{' '.join(cmd)}\n")

    return " ".join(cmd)

#!/usr/bin/env python3.12

import argparse

def cli_parser():
    """Create and configure argument parser matching TOML structure."""
    parser = argparse.ArgumentParser(
        description='Clushible (ClusterShell-ed Ansible)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
   
    core_ctl = parser.add_argument_group('Core', 'Core options') 
    core_ctl.add_argument('-c', '--config', dest='core_config', default='', help='Path to Clushible TOML configuration file')
    core_ctl.add_argument('--disable-target-validation', dest='core_disable_target_validation', action='store_true', help='Disable target nodeset validation.')
    core_ctl.add_argument('--dry-run', dest='core_dry_run', action='store_true', default=None, help='Only do a dry run of expected execution.')
    core_ctl.add_argument('--partition-only', dest='core_partition_only', action='store_true', help='Only show partitioning info.')
    core_ctl.add_argument('--debug', dest='core_debug', action='store_true', help='Set to debug mode (noop / verbose)')
    core_ctl.add_argument('-v', '--verbose', dest='core_verbose', action='count', default=0, help='Application verbosity.')
    core_ctl.add_argument('-V', '--version', dest='core_version', action='store_true', help='Show version and exit')
    core_ctl.add_argument('--aggregate-logs', dest='core_aggregate_logs', action='store_true', help='Collect and compress Ansible logs onto controller.')
    core_ctl.add_argument('--transport', dest='core_transport', choices=['nfs', 'git'], help="Use NFS backend or Git backends.")

    logging_ctl = parser.add_argument_group('Logging', 'Logging options')
    logging_ctl.add_argument('--logging-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level')
    logging_ctl.add_argument('--logging-file', help='Log file path')
   
    # Clushible-specific Arguments
    ctl_group = parser.add_argument_group('Clushible', 'Clushible Controls')
    ctl_group.add_argument('--runners', dest='clushible_runners', help='Ansible Runners (clushible children)')
    ctl_group.add_argument('--valid-targets', dest='clushible_valid_targets', help='Valid target nodeset for clushible operations.')
    ctl_group.add_argument('--fscale', dest='clushible_fscale', type=int, help='Ansible fork scaling factor when forks are 0 (auto).')
    ctl_group.add_argument('-w', '--targets', dest='clushible_target', help='Ansible target nodes (pdsh/clush format).')
    ctl_group.add_argument('-n', '--nsets', dest='clushible_sets', type=int, help='number of sets to split into.')
    ctl_group.add_argument('--distribution', dest='clushible_distribution', default=None, choices=['pack', 'scatter'], help='Pack or Scatter')
    ctl_group.add_argument('-b', dest='clushible_collate', action='store_true', default=None, help='Collate output pdsh/clubak style.')
    ctl_group.add_argument('-L', dest='clushible_coll_header', action='store_true', default=None, help='Disable collated header block (clubak -L opt)')
 
    # Ansible Core Arguments
    ansible_ctl = parser.add_argument_group('Ansible Arguments', 'Ansible Arguments')
    ansible_ctl.add_argument('--check', dest='ansible_check', action='store_true', help='Ansible check mode.')
    ansible_ctl.add_argument('-f', '--forks', dest='ansible_forks', type=int, help='Ansible forks')
    ansible_ctl.add_argument('--playbook-cmd', dest='ansible_playbook_cmd', type=str, help='Ansible playbook command location')
    ansible_ctl.add_argument('--project-dir', dest='ansible_project_dir', type=str, help='Ansible project directory')
    ansible_ctl.add_argument('-i', '--inventory', dest='ansible_inventory', type=str, help='Ansible inventory')
    ansible_ctl.add_argument('--playbook', dest='ansible_playbook', type=str, help='Ansible playbook')
    ansible_ctl.add_argument('--vault-passwd-file', dest='ansible_vault_passwd_file', type=str, help='Ansible Vault password file.')
    ansible_ctl.add_argument('--tags', dest='ansible_tags', type=str, help='Ansible tags to apply')
    ansible_ctl.add_argument('--skip-tags', dest='ansible_skip_tags', type=str, help='Ansible tags to skip')

    return parser

# Default Configuration Values

_defaults = {
    "core": {
        "config": None,
        "debug": False,
        "disable_target_validation": False,
        "dry_run": False,
        "verbose": 0,
        "partition_only": False,
        "version": False,
        "aggregate_logs": False,
        "transport": "nfs",
    },
    "clushible": {
        "runners": None,
        "valid_targets": None,
        "collate": False,
        "coll_header": False,
        "distribution": "scatter",  # scatter or pack
        "fscale": 4,
        "sets": 0,
        "target": None,
    },
    "ansible": {
        "check": False,
        "playbook_cmd": None,
        "project_dir": None,
        "inventory": None,
        "playbook": None,
        "vault_passwd_file": None,
        "forks": 0,  # Auto-sense
        "tags": "",
        "skip_tags": "",
    },
    "logging": {
        "aggregate_logs": False,
        "level": 0,
        "file": None,
    },
}


def set_defaults(conf: dict) -> None:
    # This is not to find errors, only apply critical defaults
    # Coverage for None and emtpy string
    empty = {None, ""}

    # Check critials for empty specifics:
    # Maybe just do ALL of them in the long run
    for s, opts in conf.items():
        for opt in opts.keys():
            if conf[s][opt] in empty:
                conf[s][opt] = _defaults[s][opt]

    # for s,v in checks:
    #    if conf[s][v] in empty:
    #        conf[s][v] = _defaults[s][v]

    # if conf.clushible.fscale in empty:
    #    conf.clushible.fscale = _defaults["clushible"]["fscale"]

    # if conf.clushible.distribution in empty:
    #    conf.clushible.distribution = _defaults["clushible"]["distribution"]

    # if conf.ansible.forks in empty:
    #    conf.ansible.forks = _defaults["ansible"]["forks"]

    return None

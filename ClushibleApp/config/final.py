#!/usr/bin/env python3.12

# Load Modules
import os
import sys

from pathlib import Path
from types import SimpleNamespace

# Load Local Modules
from . import cli
from . import file
from .defaults import set_defaults
from ..utils import msg

def __to_namespace(d):
    """Recursively converts a dictionary (and its nested dicts) to SimpleNamespace."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: __to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [__to_namespace(elem) for elem in d]
    else:
        return d

def __to_empty_dict(N):
    """Returns an empty-value dictionary representation of argparse namespace."""
    d = {}
    #for g in N.parser.
    return d

def get_config():
    cli_p = cli.cli_parser()
    cli_ns = cli_p.parse_args()
    cli_dict = vars(cli_ns)

    # Generate a ref structure based on argparse namespace
    ref_args = {}
    cli_args = {}
    for k in cli_dict.keys():
        section,opt = k.split('_',1)

        if section not in ref_args.keys():
            ref_args[section] = {}

        if section not in cli_args.keys():
            cli_args[section] = {}

        ref_args[section][opt] = ""
        cli_args[section][opt] = cli_dict[f"{section}_{opt}"]

    c_locs = [
            cli_ns.core_config, 
            os.environ['CLUSHIBLE_CONFIG'] if 'CLUSHIBLE_CONFIG' in os.environ.keys() else "", 
            '/etc/clushible.toml',
            f'{sys.prefix}/etc/clushible.toml']
    c_locs[:] = [p for p in c_locs if p]

    c = Path(c_locs.pop(0))
    while not c.exists():
        if cli_ns.core_verbose > 2:
            msg.info(f"Popping {c} from config list as not found.")
        if len(c_locs) == 0:
            msg.error("No suitable configuration file found.")
        c = Path(c_locs.pop(0))
        #msg.error(f"{c} config file does not exists. Exiting.")
        #sys.exit(1)

    #cli_args['core']['config'] = str(c)

    # Load TOML config
    file_args = file.load_config(c)

    # Create a fixed structure copy to return, should be mostly empty, but may need deep copy later
    final_args = ref_args.copy()

    # Set Defaults
    set_defaults(final_args)

    # Iterate over sections and key,values that match structure from config file
    for section,opts in file_args.items():
        if section not in final_args.keys():
            msg.warn(f"Section '[{section}]' in TOML config is not used. Skipping.")
            continue
        for k,v in opts.items():
            # Alias because I'm lazy
            o = final_args[section]
            if k not in o.keys():
                msg.warn(f"Parameter '{k}' not valid in '[{section}]' section")
                continue
            o[k] = v

    # Iterate over sections and key,values that match cli
    for section,opts in cli_args.items():
       for k,v in opts.items():
           if v is not None:
               final_args[section][k] = v
    final_args['core']['config'] = str(c)

    # Apply Defaults to unsets (arguably, this should be applied earlier)
    #set_defaults(final_args)
    conf_namespace = __to_namespace(final_args)
    

    # Return as namespaced
    return conf_namespace


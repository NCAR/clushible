#

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions

from pprint import pprint

from .._version import __version__


_type_map = {
    "str": str,
    "int": int,
    "bool": bool,
    "list": list,
    "float": float,
    "dict": dict,
    "Any": Any,
    "any": Any,
}


@dataclass
class ArgumentOption:
    name: list
    dest: str
    help: str
    action: str = None
    default: Any = None
    type: Any = None
    choices: list = None
    example: Any = None
    internal_default: Any = None
    file_option: bool = True
    cli_option: bool = True


def _dict_to_namespace(d: dict) -> SimpleNamespace:
    """Recursively converts a dictionary (and its nested dicts) to SimpleNamespace."""
    if isinstance(d, dict):
        return SimpleNamespace(
            **{k: _dict_to_namespace(v) for k, v in d.items()}
        )
    elif isinstance(d, list):
        return [_dict_to_namespace(elem) for elem in d]
    else:
        return d


def _load_toml_opts():
    """
    Docstring for _load_toml_opts
    """
    opts_file = Path(__file__).parent / "options.toml"
    with opts_file.open("rb") as f:
        data = tomllib.load(f)

    return data


def _generate_argument_options():
    """Generate argument options from the TOML configuration."""
    config_data = _load_toml_opts()
    argument_options = dict()

    for section, options in config_data.items():
        argument_options[section] = dict()
        for option_key, option_values in options.items():
            argument_option = ArgumentOption(
                name=option_values.get("name", []),
                dest=f"{section}_{option_key}",
                help=option_values.get("help", ""),
                action=option_values.get("action", None),
                default=option_values.get("default", None),
                type=_type_map[option_values.get("type", "Any")],
                choices=option_values.get("choices"),
                example=option_values.get("example", "None"),
                internal_default=option_values.get("internal_default", None),
                file_option=option_values.get("file_option", True),
                cli_option=option_values.get("cli_option", True),
            )
            argument_options[section][option_key] = argument_option

    return argument_options


def _generate_cli_parser():
    """Generate the CLI parser based on argument options."""

    # dictionary of section -> ArgumentOption(s)
    args_dict = _generate_argument_options()

    parser = argparse.ArgumentParser(
        prog="Clushible",
        description="Clushible (ClusterShell-ed Ansible)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    for section, options in args_dict.items():
        group = parser.add_argument_group(
            section.capitalize(), f"{section.capitalize()} Options"
        )
        for option_key, option in options.items():
            kwargs = {
                "dest": option.dest,
                "help": option.help,
            }

            # If action is specific, don't specify type
            if option.action:
                kwargs["action"] = option.action
                if option.action in {"count", "store_true", "store_false"}:
                    pass
                else:
                    if option.type:
                        kwargs["type"] = option.type

            if option.default not in {None, "None"}:
                kwargs["default"] = option.default
            else:
                kwargs["default"] = argparse.SUPPRESS

            if option.choices:
                kwargs["choices"] = option.choices

            group.add_argument(*option.name, **kwargs)

    return parser


def _dump_config_template():
    """Dump a configuration template based on the argument options."""
    args_dict = _generate_argument_options()

    config_lines = ["# Example Clushible Configuration File\n"]

    for section, options in args_dict.items():
        config_lines.append(f"[{section}]")
        for option_key, option in options.items():
            # Use example if available
            value = None
            if option.file_option is False:
                continue
            try:
                # This is as bit silly, but we'll just try to access and if
                # fail, move on.
                option.example
                value = option.example
            except AttributeError:
                try:
                    option.default
                    if option.default not in {None, "None"}:
                        value = option.default
                except AttributeError:
                    pass

            # If an internal default is defined, use that instead.
            try:
                option.internal_default
                if value is None:
                    value = option.internal_default
            except AttributeError:
                pass

            if isinstance(value, str):
                value = f'"{value}"'

            if isinstance(value, bool):
                value = f"{str(value).lower()}"

            if value is None:
                value = '"None"'

            config_lines.append(f"# {option.help}")
            config_lines.append(f"#{option_key} = {value}\n")

        config_lines.append("")

    return "\n".join(config_lines)


def _load_config(config_path: Path) -> dict:
    """Load and parse TOML configuration file."""
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(
            f"Error: Configuration file '{config_path}' not found.",
            file=sys.stderr,
        )
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"Error: Invalid TOML in '{config_path}': {e}", file=sys.stderr)
        sys.exit(1)


def _get_cli_args() -> argparse.Namespace:
    args = _generate_cli_parser()
    pargs = args.parse_args()
    return pargs


def _construct_default_config() -> dict:
    config_dict = _load_toml_opts()
    default_config = dict()
    # pprint(config_dict)
    for section, options in config_dict.items():
        default_config[section] = dict()
        for option_key, option_values in options.items():
            int_default = option_values.get("internal_default", None)
            if int_default not in {None, "None"}:
                default_config[section][option_key] = int_default
            else:
                default_config[section][option_key] = ""

            # print(f"{section}.{option_key} = {int_default}")
    return default_config


def _overlay_config_files(config: dict, config_files: list[str] = []) -> None:
    if len(config_files) == 0:
        if "CLUSHIBLE_CONFIG" in os.environ.keys():
            config_files.append(os.environ["CLUSHIBLE_CONFIG"])
        config_files.append("/etc/clushible.toml")
        config_files.append(f"{sys.prefix}/etc/clushible.toml")

    config_files[:] = [p for p in config_files if p]

    c = Path(config_files.pop(0))
    while not c.exists():
        print(f"Popping {c} from config list as not found.")
        c = Path(config_files.pop(0))
        if len(config_files) == 0:
            print("No suitable configuration file found. Using defaults only.")
            return config

    toml_conf = _load_config(c)
    for section, opts in toml_conf.items():
        if section not in config.keys():
            print(
                f"Section '[{section}]' in TOML config is not used. Skipping."
            )
            continue
        for k, v in opts.items():
            # Alias because I'm lazy
            o = config[section]
            if k not in o.keys():
                print(f"Parameter '{k}' not valid in '[{section}]' section")
                continue
            o[k] = v


def _overlay_cli_args(config: dict, cli_args: argparse.Namespace):
    for section, opts in vars(cli_args).items():
        sec, opt = section.split("_", 1)
        config[sec][opt] = opts


def _pre_process_cli_args(args: argparse.Namespace) -> None:
    """Pre-process CLI args if needed."""

    if hasattr(args, "core_version") and args.core_version:
        print(f"Clushible {__version__}")
        sys.exit(0)

    if (
        hasattr(args, "core_dump_config_template")
        and args.core_dump_config_template
    ):
        print(_dump_config_template())
        sys.exit(0)


def _get_config(args: argparse.Namespace) -> dict:
    """Get the final configuration by overlaying defaults, config files, and CLI args."""
    config = _construct_default_config()

    _pre_process_cli_args(args)

    # Overlay config files
    try:
        if args.core_config:
            config_files = [args.core_config]
    except AttributeError:
        config_files = []

    _overlay_config_files(config, config_files)

    # Overlay CLI args
    _overlay_cli_args(config, args)

    return config


CONFIG = _dict_to_namespace(_get_config(_get_cli_args()))

# Main block for testing purposes for now
if __name__ == "__main__":
    pass
    # pprint(CONFIG)
    # args = _get_cli_args()
    # _get_config(args)
    # print(construct_default_config())
    # print(dump_config_template())


import sys
from pathlib import Path
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions


def load_config(config_path):
    """Load and parse TOML configuration file."""
    try:
        with open(config_path, 'rb') as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"Error: Invalid TOML in '{config_path}': {e}", file=sys.stderr)
        sys.exit(1)



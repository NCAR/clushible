#!/opt/clmgr/python-310/bin/python3.10

import sys
import time

import configparser

config = configparser.ConfigParser()

# Set some defaults here, then overwrite them later by either config file or flags
config["default"] = {
        "limit": "@mtn:all",
        "vault_passwd_file": "/root/ansible.passwd",
        "log_method": "segmented",
        "check_mode": "false",
        }

config.read("./clushible.cfg")

if __name__ == "__main__":
    print(config.sections())
    for i in config.sections():
        for j in config[i].items():
            print(type(j),"--",j)
    sys.exit(0)

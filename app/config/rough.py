#!/usr/bin/env python
"""
Seshat config for daemons to use during start up

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import os
import sys
import yaml

def rough_parse_config(name=None):
    abspath = os.path.dirname(__file__)
    path = abspath.rsplit("config", 1)[0]
    sys.path.append(path)
    os.chdir(path)
    current_path = os.getcwd() + "/"

    config = yaml.load(file(current_path+"config/config.yaml", 'r'))
    if name:
        config = config[name]

    for directory in config["dirs"]:
        if config["dirs"][directory][0] != "/":
            direct = current_path + config["dirs"][directory]
        else:
            direct = config["dirs"][directory]
        if not os.path.exists(direct):
            os.makedirs(direct)
        config["dirs"][directory] = direct

    for fi in config["files"]:
        extension = config["files"][fi].rsplit(".", 1)
        if "pid" in extension:
            config["files"][fi] = config["dirs"]["pid"] + config["files"][fi]
        elif "log" in extension:
            config["files"][fi] = config["dirs"]["log"] + config["files"][fi]

    return config


def setup_log(name=None):
    """
    Sets up the main logger for the daemon
    """
    import logging
    import config as c
    level = logging.WARNING
    if c.debug:
            level = logging.DEBUG

    formatter = logging.Formatter("""%(asctime)s - %(name)s - %(levelname)s
    %(message)s""")

    logger = logging.getLogger()
    logger.setLevel(level)

    if not name:
        fh = logging.FileHandler(c.files.log)
    else:
        name = getattr(c, name)
        fh = logging.FileHandler(name.files.log)

    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if c.debug:
        """
        Make sure we're not in daemon mode if we're logging to console too
        """
        try:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        except:
            pass

    return logger

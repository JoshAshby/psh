#!/usr/bin/env python
"""
Seshat config

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import os
import yaml
import redis as red
import rethinkdb as r
import docker as d

from utils.standard import StandardODM


"""
#########################STOP EDITING#####################################
***WARNING***
Don't change these following settings unless you know what you're doing!!!
##########################################################################
"""

current_path = os.path.dirname(__file__) + "/"
base_path = current_path.rsplit("config")[0]

general = None
with open(current_path + "config.yaml", "r") as open_config:
    general = StandardODM(**yaml.load(unicode(open_config.read())))

if not general:
    raise Exception("Could not load config.yaml into StandardODM!")


def parse_files(conf):
    if "dirs" in conf:
        for directory in conf.dirs:
            if conf.dirs[directory][0] != "/":
                direct = base_path + conf.dirs[directory]
            else:
                direct = conf.dirs[directory]
            if not os.path.exists(direct):
                os.makedirs(direct)
            conf.dirs[directory] = direct

    if "files" in conf:
        for fi in conf.files:
            extension = conf.files[fi].rsplit(".", 1)
            if "pid" in extension:
                conf.files[fi] = conf.dirs["pid"] + conf.files[fi]
            elif "log" in extension:
                conf.files[fi] = conf.dirs["log"] + conf.files[fi]


rethink = r.connect(db=general["databases"]["rethink"]["db"]).repl()
redis = red.StrictRedis(general["databases"]["redis"]["URL"], db=general["databases"]["redis"]["db"])

docker_url = ":".join([general["docker"]["url"], str(general["docker"]["port"])])
docker = d.Client(base_url=docker_url,
                  version=str(general["docker"]["version"]),
                  timeout=general["docker"]["timeout"])
del docker_url

parse_files(general)

builder = StandardODM(**general.builder)
parse_files(builder)

spinner = StandardODM(**general.spinner)
parse_files(spinner)

dirs = StandardODM(**general.dirs)
files = StandardODM(**general.files)

debug = general["debug"]

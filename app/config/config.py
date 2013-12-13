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
import redis
import rethinkdb
import docker

from standard import StandardConfig


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
    general = StandardConfig(**yaml.load(unicode(open_config.read())))

if not general:
    raise Exception("Could not load config.yaml into StandardConfig!")


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


rethink = rethinkdb.connect(db=general["databases"]["rethink"]["db"]).repl()
redis = redis.StrictRedis(general["databases"]["redis"]["URL"], db=general["databases"]["redis"]["db"])

docker_url = ":".join([general["docker"]["url"], str(general["docker"]["port"])])
docker = docker.Client(base_url=docker_url,
                       version=str(general["docker"]["version"]),
                       timeout=general["docker"]["timeout"])
del docker_url

parse_files(general)

builder = StandardConfig(**general.builder)
parse_files(builder)

spinner = StandardConfig(**general.spinner)
parse_files(spinner)

dirs = StandardConfig(**general.dirs)
files = StandardConfig(**general.files)

debug = general["debug"]

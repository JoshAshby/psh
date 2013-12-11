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
#from gevent_zeromq import zmq

from standard import StandardConfig

from seshat.routeTable import RouteTable

#context = zmq.Context()
#zmqSock = context.socket(zmq.PUB)

current_path = os.path.dirname(__file__) + "/"
base_path = current_path.rsplit("config")[0]

general = None
with open(current_path + "config.yaml", "r") as open_config:
    general = StandardConfig(**yaml.load(unicode(open_config.read())))

if not general:
    raise Exception("Could not load config.yaml into StandardConfig!")

general["rethink"] = rethinkdb.connect(db=general["databases"]["rethink"]["db"]).repl()
general["redis"] = redis.StrictRedis(general["databases"]["redis"]["URL"], db=general["databases"]["redis"]["db"])
#general["zeromq"] = zmqSock.bind(general["sockets"]["zeromq"]["URL"]+":"+str(general["sockets"]["zeromq"]["port"]))

for directory in general.dirs:
    if general.dirs[directory][0] != "/":
        direct = base_path + general.dirs[directory]
    else:
        direct = general.dirs[directory]
    if not os.path.exists(direct):
        os.makedirs(direct)
    general.dirs[directory] = direct


for fi in general.files:
    extension = general.files[fi].rsplit(".", 1)
    if "pid" in extension:
        general.files[fi] = general.dirs["pid"] + general.files[fi]
    elif "log" in extension:
        general.files[fi] = general.dirs["log"] + general.files[fi]

"""
#########################STOP EDITING#####################################
***WARNING***
Don't change these following settings unless you know what you're doing!!!
##########################################################################
"""
urls = RouteTable()

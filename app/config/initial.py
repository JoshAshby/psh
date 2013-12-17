#!/usr/bin/env python
"""
Initial settings for setting up the app

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
"""
First we need to import pythons regex module.
This is used by Seshat to build the routing
table according to what you dictate as the URL
regex below
"""
import os
import yaml

from utils.standard import StandardODM

current_path = os.getcwd() + "/config/"

general = None
with open(current_path + "initial.yaml", "r") as open_config:
    general = StandardODM(**yaml.load(unicode(open_config.read())))

if not general:
    raise Exception("Could not load config.yaml into StandardODM!")

#!/usr/bin/env python
"""

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import os
import subprocess

base = os.path.realpath(__file__).rsplit("/", 1)[0]

for top, folders, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
  for filename in files:
    if filename[0] not in ["~", "."]:
      name, extension = filename.split(".", 1)

      if extension == "less" and name not in ["base", "colors", "flexbox", "lesshat"]:
        folder = top.split(base)[1].strip("/")
        if folder:
            path = os.path.realpath("/".join([folder, filename]))
            name = "/".join([folder, name])
            print "Compiling {folder}/{filename} to {name}.css".format(name=name, filename=filename, folder=folder)
        else:
            path = os.path.realpath(filename)
            print "Compiling {filename} to {name}.css".format(name=name, filename=filename, folder=folder)
        subprocess.call("lessc {path} > ../css/{name}.css".format(name=name, path=path), shell=True)

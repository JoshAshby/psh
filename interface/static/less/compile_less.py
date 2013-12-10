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

for top, folders, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
  for filename in files:
    if filename[0] not in ["~", "."]:
      name, extension = filename.split(".", 1)

      if extension == "less" and name not in ["base", "colors", "flexbox", "lesshat"]:
         path = os.path.realpath(filename)
         print "Compiling {filename} to {name}.css".format(name=name, filename=filename)
         subprocess.call("lessc {path} > ../css/{name}.css".format(name=name, path=path), shell=True)

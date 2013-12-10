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

      if extension == "coffee" and name not in []:
         path = os.path.realpath(filename)
         print "Compiling {filename} to {name}.js".format(name=name, filename=filename)
         subprocess.call("coffee -c -o ../js/ {path}".format(name=name, path=path), shell=True)

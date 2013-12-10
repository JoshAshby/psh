#!/usr/bin/env python
"""
Imports all the controllers automatically
Takes care of adding new controllers, and coupled
with the autoRouter, makes adding new pages and
controllers a breeze.

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""

import os
which = ""
path = os.path.dirname(__file__)
for folder in os.walk(path):
    if "__init__.py" not in folder[2]:
        # Don't import anything from folders that do not have an __init__.py
        pass
    else:
        base = folder[0][len(path):].replace("/", ".").strip(".")
        if len(base) > 0:
            which = "controllers." + base + "."
        else:
            which = "controllers."
        for module in folder[2]:
            if module == '__init__.py' \
                    or module[-3:] != '.py' \
                    or module == 'controllerMap.py':
                        continue
            module = module[:-3]
            fullname = which + module
            __import__(fullname, locals(), globals(), ['*'])
            for k in dir(fullname):
                locals()[k] = getattr(fullname, k)
del module

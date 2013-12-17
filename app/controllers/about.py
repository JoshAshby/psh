#!/usr/bin/env python
"""

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.route import autoRoute
from seshat.MixedObject import MixedObject


@autoRoute()
class about(MixedObject):
    _title = "about"
    _default_tmpl = "public/about/about"
    def GET(self):
        return self.view

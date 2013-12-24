#!/usr/bin/env python
"""
main index - reroutes to login if you're not logged in

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.route import autoRoute
from seshat.MixedObject import MixedObject
from seshat.objectMods import login


@login(redirect="/login")
@autoRoute()
class index(MixedObject):
    _title = "Home"
    _default_tmpl = "public/index/index"
    def GET(self):
        self.view.partial("sidebar", "partials/public/sidebar_links",
                          {"command": "home"})
        return self.view

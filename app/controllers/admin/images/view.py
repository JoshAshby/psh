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
from seshat.objectMods import login

from seshat.actions import NotFound
from errors.general import NotFoundError

from models.rethink.image import imageModel as im


@login(["admin"])
@autoRoute()
class view(MixedObject):
    _title = "Images"
    _default_tmpl = "admin/images/view"
    def GET(self):
        self.view.partial("sidebar", "partials/admin/sidebar_links",
                          {"command": "images"})
        try:
            image = im.Image(self.request.id)
        except NotFoundError:
            return NotFound()

        self.view.title = image.name

        self.view.data = {"image": image}

        return self.view

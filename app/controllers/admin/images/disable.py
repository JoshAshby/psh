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

from seshat.actions import NotFound, Redirect
from errors.general import NotFoundError

from models.rethink.image import imageModel as im


@login(["admin"])
@autoRoute()
class disable(MixedObject):
    def POST(self):
        if not self.request.id:
            return Redirect("/admin/images")

        try:
            image = im.Image(self.request.id)
        except NotFoundError:
            return NotFound()

        image.disable = not image.disable
        image.save()

        return Redirect("/admin/images/"+self.request.id)

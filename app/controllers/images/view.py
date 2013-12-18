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

from seshat.actions import NotFound, Unauthorized
from errors.general import NotFoundError

from models.rethink.image import imageModel as im



@login()
@autoRoute()
class view(MixedObject):
    _title = "Images"
    _default_tmpl = "public/images/index"
    def GET(self):
        try:
            image = im.Image(self.request.id)
        except NotFoundError:
            return NotFound()

        if not self.request.session.has_admin or \
            (image.user_id!=self.request.session.id):
              return Unauthorized()

        if image.disable:
            self.view.template = "public/images/disabled"
            return self.view

        self.view.template = "public/images/view"

        self.view.title = image.name

        self.view.data = {"image": image,}

        return self.view

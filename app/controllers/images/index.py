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
from seshat.baseObject import MixedObject
from seshat.objectMods import login

from seshat.actions import NotFound, Unauthorized
from errors.general import NotFoundError

import rethinkdb as r
from rethinkORM import RethinkCollection

from models.rethink.image import imageModel as im

from utils.paginate import Paginate


@login()
@autoRoute()
class index(MixedObject):
    _title = "Images"
    _default_tmpl = "public/images/index"
    def GET(self):
        if not self.request.id:
            q = r.table(im.Image.table).filter({"user": self.request.session.id})
            res = RethinkCollection(im.Image, query=q)
            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                image = im.Image(self.request.id)

            except NotFoundError:
                return NotFound()

            if not self.request.session.has_admin and \
                (image.user != self.request.session.id):
                  return Unauthorized()

            self.view.template = "public/images/view"

            self.request.title = image.name

            self.view.data = {"image": image}

            return self.view

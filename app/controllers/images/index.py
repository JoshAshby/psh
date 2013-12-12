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

from rethinkORM import RethinkCollection

from models.rethink.image import imageModel as im

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login()
@autoRoute()
class index(MixedObject):
    _title = "Images"
    _default_tmpl = "public/images/index"
    def GET(self):
        if not self.request.id:
            q = dbu.rql_where_not(im.Image.table, "disable", True).filter({"user": self.request.session.id})
            res = RethinkCollection(im.Image, query=q)
            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                image = im.Image(self.request.id)
            except NotFoundError:
                return NotFound()

            if not self.request.session.has_admin or \
                (image.user != self.request.session.id):
                  return Unauthorized()

            if image.disable:
                self.view.template = "public/images/disabled"
                return self.view

            self.view.template = "public/images/view"

            self.request.title = image.name

            self.view.data = {"image": image}

            return self.view

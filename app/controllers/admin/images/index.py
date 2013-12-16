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

from seshat.actions import NotFound, Redirect
from errors.general import NotFoundError

from rethinkORM import RethinkCollection

from models.rethink.image import imageModel as im

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Images"
    _default_tmpl = "admin/images/index"
    def GET(self):
        if not self.request.id:
            disabled = self.request.getParam("d", True)
            if disabled:
                q = dbu.rql_where_not(im.Image.table, "disable", True)
                res = RethinkCollection(im.Image, query=q)
            else:
                res = RethinkCollection(im.Image)

            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                image = im.Image(self.request.id)
            except NotFoundError:
                return NotFound()

            self.view.template = "admin/images/view"

            self.request.title = image.name

            self.view.data = {"image": image}

            return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/admin/images")

        try:
            image = im.Image(self.request.id)
        except NotFoundError:
            return NotFound()

        if self.request.command == "disable":
            image.disable = not image.disable
            image.save()

        return Redirect("/admin/images/"+self.request.id)

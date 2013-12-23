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
        self.view.partial("sidebar", "partials/admin/sidebar_links",
                          {"command": "images"})
        disabled = self.request.getParam("d", True)
        if disabled:
            q = dbu.rql_where_not(im.Image.table, "disable", True)
            res = RethinkCollection(im.Image, query=q)
        else:
            res = RethinkCollection(im.Image)

        page = Paginate(res, self.request, "name")

        self.view.data = {"page": page}

        return self.view

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

from models.rethink.container import containerModel as cm

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Containers"
    _default_tmpl = "admin/containers/index"
    def GET(self):
        self.view.partial("sidebar", "partials/admin/sidebar_links",
                          {"command": "containers"})
        disabled = self.request.getParam("d", True)
        if disabled:
            q = dbu.rql_where_not(cm.Container.table, "disable", True)
            res = RethinkCollection(cm.Container, query=q)
        else:
            res = RethinkCollection(cm.Container)

        page = Paginate(res, self.request, "name")

        self.view.data = {"page": page}

        return self.view

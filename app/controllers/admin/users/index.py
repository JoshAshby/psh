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
from models.rethink.user import userModel as um

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Users"
    _default_tmpl = "admin/users/index"
    def GET(self):
        disabled = self.request.getParam("d", True)
        if disabled:
            q = dbu.rql_where_not(um.User.table, "disable", True)
            res = RethinkCollection(um.User, query=q)

        else:
            res = RethinkCollection(um.User)

        page = Paginate(res, self.request, "username")

        self.view.data = {"page": page}

        return self.view

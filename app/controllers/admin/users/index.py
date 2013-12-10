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
from seshat.baseObject import HTMLObject
from seshat.objectMods import login

from rethinkORM import RethinkCollection
from models.rethink.user import userModel as um
from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class index(HTMLObject):
    _title = "Users"
    _defaultTmpl = "admin/users/index"
    def GET(self):
        q = dbu.rql_where_not(um.User.table, "disable", False)
        res = RethinkCollection(um.User, query=q)
        page = Paginate(res, self.request, "username")

        self.view.data = {"page": page}

        return self.view

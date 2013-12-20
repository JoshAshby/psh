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

import rethinkdb as r
from rethinkORM import RethinkCollection
from models.rethink.user import userModel as um
from models.rethink.image import imageModel as im
from models.rethink.container import containerModel as cm

from utils.paginate import Paginate


@login(["admin"])
@autoRoute()
class containers(MixedObject):
    _title = "Users"
    _default_tmpl = "admin/users/containers"
    def GET(self):
            try:
                user = um.User(self.request.id)

            except NotFoundError:
                return NotFound()

            self.view.title = user.username

            imgs = r.table(im.Image.table).filter({"user_id": user.id})\
                .count().run()
            cons = r.table(cm.Container.table).filter({"user_id": user.id})\
                .count().run()

            self.view.partial("tabs",
                              "partials/admin/users/tabs",
                              {"user": user,
                               "command": self.request.command,
                               "images": imgs,
                               "containers": cons})

            self.view.data = {"user": user}

            q= r.table(cm.Container.table).filter({"user_id": user.id})
            cons = RethinkCollection(cm.Container, query=q)
            page = Paginate(cons, self.request, "name")

            self.view.data = {"page": page}

            return self.view

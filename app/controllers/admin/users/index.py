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

import rethinkdb as r
from rethinkORM import RethinkCollection
from models.rethink.user import userModel as um
from models.rethink.image import imageModel as im
from models.rethink.container import containerModel as cm

from models.utils import dbUtils as dbu
from utils.paginate import Paginate

commands = [
    None,
    "emails",
    "images",
    "containers"
    ]


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Users"
    _default_tmpl = "admin/users/index"
    def GET(self):
        if not self.request.id:
            disabled = self.request.getParam("d", True)
            if disabled:
                q = dbu.rql_where_not(um.User.table, "disable", True)
                res = RethinkCollection(um.User, query=q)

            else:
                res = RethinkCollection(um.User)

            page = Paginate(res, self.request, "username")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                user = um.User(self.request.id)

            except NotFoundError:
                return NotFound()

            if self.request.command not in commands:
                return NotFound()

            if not self.request.command:
                self.view.template = "admin/users/settings"

            else:
                self.view.template = "admin/users/"+self.request.command

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

            if self.request.command == "images":
                q= r.table(im.Image.table).filter({"user_id": user.id})
                images = RethinkCollection(im.Image, query=q)
                page = Paginate(images, self.request, "name")

                self.view.data = {"page": page}

            if self.request.command == "containers":
                q= r.table(cm.Container.table).filter({"user_id": user.id})
                cons = RethinkCollection(cm.Container, query=q)
                page = Paginate(cons, self.request, "name")

                self.view.data = {"page": page}

            return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/admin/users/")

        if self.request.command not in commands:
            return NotFound()

        try:
            user = um.User(self.request.id)
        except NotFoundError:
            return NotFound()

        if not self.request.command:
            password = self.request.getParam("password")
            disable = self.request.getParam("disable", False)

            if password:
                user.set_password(password)

            user.disable = disable

            user.save()

        return Redirect("/admin/users/"+self.request.id_extended)

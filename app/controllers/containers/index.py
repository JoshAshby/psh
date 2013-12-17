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
from seshat.actions import Redirect

from seshat.actions import NotFound, Unauthorized
from errors.general import NotFoundError

from rethinkORM import RethinkCollection
from models.rethink.container import containerModel as cm

from models.utils import dbUtils as dbu
from utils.paginate import Paginate


@login()
@autoRoute()
class index(MixedObject):
    _title = "Containers"
    _default_tmpl = "public/containers/index"
    def GET(self):
        if not self.request.id:
            q = dbu.rql_where_not(cm.Container.table, "disable", True)\
                .filter({"user_id": self.request.session.id})

            res = RethinkCollection(cm.Container, query=q)
            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                con = cm.Container(self.request.id)
            except NotFoundError:
                return NotFound()

            if not self.request.session.has_admin or \
                (con.user_id!=self.request.session.id):
                  return Unauthorized()

            if con.disable:
                self.view.template = "public/containers/disabled"
                return self.view

            self.view.template = "public/containers/view"

            self.view.title = con.name

            self.view.data = {"container": con}

            return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/containers")

        else:
            try:
                con = cm.Container(self.request.id)
            except NotFoundError:
                return NotFound()

            if not self.request.session.has_admin or \
                (con.user_id!=self.request.session.id):
                  return Unauthorized()

            if con.disable:
                self.view.template = "public/containers/disabled"
                return self.view

            if self.request.command == "update":
                ports = {}
                p = con.image.ports
                for port in p:
                    ports[port] = self.request.getParam("port_"+port, None)

                con.update_ports(ports)

            if self.request.command == "start":
                con.queue_action("start")
                return {"status": "success"}

            if self.request.command == "restart":
                con.queue_action("restart")
                return {"status": "success"}

            if self.request.command == "stop":
                con.queue_action("stop")
                return {"status": "success"}

            if self.request.command == "status":
                return {"status": con.status}

            return Redirect("/containers/"+con.id)

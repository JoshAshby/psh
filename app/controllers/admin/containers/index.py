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
        if not self.request.id:
            disabled = self.request.getParam("d", True)
            if disabled:
                q = dbu.rql_where_not(cm.Container.table, "disable", True)
                res = RethinkCollection(cm.Container, query=q)
            else:
                res = RethinkCollection(cm.Container)

            page = Paginate(res, self.request, "name")

            self.view.data = {"page": page}

            return self.view
        else:
            try:
                con = cm.Container(self.request.id)
            except NotFoundError:
                return NotFound()

            self.view.template = "admin/containers/view"

            self.view.title = con.name

            self.view.data = {"container": con}

            return self.view

    def POST(self):
        if not self.request.id:
            return Redirect("/admin/containers")

        try:
            con = cm.Container(self.request.id)
        except NotFoundError:
            return NotFound()

        if self.request.command == "disable":
            con.disable = not con.disable
            con.queue_action("stop")
            con.save()

        if self.request.command == "update":
            ports = {}
            p = con.image.ports
            for port in p:
                ports[port] = self.request.getParam("port_"+port, None)

            con.update_ports(ports)

        return Redirect("/admin/containers/"+self.request.id)

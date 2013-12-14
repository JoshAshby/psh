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
from seshat.actions import Redirect

from models.rethink.container import containerModel as cm
from models.rethink.image import imageModel as im
from models.rethink.dockerfile import dockerfileModel as dfm
from rethinkORM import RethinkCollection
from models.utils import dbUtils as dbu


@login()
@autoRoute()
class container(MixedObject):
    _title = "New Container - Step 1"
    _default_tmpl = "public/new/container_step_1"
    def GET(self):
        if self.request.id == "step-1" or not self.request.id:
            q = dbu.rql_where_not(im.Image.table, "disable", True).filter({"user": self.request.session.id}).order_by("name")
            q = dbu.rql_highest_revs(q, "dockerfile")
            res = RethinkCollection(im.Image, query=q).fetch()
            self.view.data = {"images": res}

        elif self.request.id == "step-2":
            if not "c_name" in self.request.session:
                self.request.session.push_alert("Missing vital info (Please fill out a name for the container before procceding to step 2)!", level="error")
                return Redirect("/new/container/step-1")

            ports = dfm.Dockerfile(im.Image(self.request.session.c_image).dockerfile).ports
            self.request.title = "New Container - Step 2"
            self.view.template = "public/new/container_step_2"
            self.view.data = {"ports": ports}

        return self.view

    def POST(self):
        if self.request.id == "step-1" or not self.request.id:
            name = self.request.getParam("name")
            image = self.request.getParam("image")

            self.request.session.c_image = image
            self.request.session.c_name = name

            return Redirect("/new/container/step-2")

        elif self.request.id == "step-2":
            if not "c_name" in self.request.session:
                self.request.session.push_alert("Missing vital info (Please fill out a name for the container before procceding to step 2)!", level="error")
                return Redirect("/new/container/step-1")

            domain = self.request.getParam("domain")

            ports = {}
            p = dfm.Dockerfile(im.Image(self.request.session.c_image).dockerfile).ports
            for port in p:
                print port
                ports[port] = self.request.getParam("port_"+port, None)

            print ports

            container = cm.Container.new_container(user=self.request.session.id,
                                                   name=self.request.session.c_name,
                                                   img=self.request.session.c_image,
                                                   ports = ports,
                                                   hostname=domain)

            del self.request.session.c_name
            del self.request.session.c_image

            return Redirect("/containers/"+container.id)

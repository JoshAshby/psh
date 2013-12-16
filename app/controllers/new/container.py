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

import rethinkdb as r
from rethinkORM import RethinkCollection
from models.rethink.image import imageModel as im
from models.rethink.container import containerModel as cm
from models.utils import dbUtils as dbu


@login()
@autoRoute()
class container(MixedObject):
    _title = "New Container - Step 1"
    _default_tmpl = "public/new/container_step_1"
    def GET(self):
        if self.request.id == "step-1" or not self.request.id:
            q = dbu.rql_where_not(im.Image.table, "disable", True)\
                .filter({"user_id": self.request.session.id}).order_by("name")
            q = dbu.rql_highest_revs(q, "name")
            res = RethinkCollection(im.Image, query=q).fetch()

            if not res:
                self.request.session.push_alert("You have no images to make a container from. Please create an image first by uploading a Dockerfile to build.")
                return Redirect("/new")

            self.view.data = {"images": res}

        elif self.request.id == "step-2":
            if not "c_name" in self.request.session:
                self.request.session.push_alert("Missing vital info (Please fill out a name for the container before procceding to step 2)!", level="error")
                return Redirect("/new/container/step-1")

            ports = im.Image(self.request.session.c_image).ports
            self.request.title = "New Container - Step 2"
            self.view.template = "public/new/container_step_2"
            self.view.data = {"ports": ports}

        return self.view

    def POST(self):
        if self.request.id == "step-1" or not self.request.id:
            name = self.request.getParam("name")
            image = self.request.getParam("image")

          # TODO: Return if name is already used

            found = r.table(cm.Container.table)\
                .filter({"user_id": self.request.session.id, "name": name})\
                .count().run()

            if found:
                self.view.data = {
                    "error": "name",
                    "msg": "You already have a container by that name! Please choose a different one."
                }
                return self.view

            self.request.session.c_image = image
            self.request.session.c_name = name

            return Redirect("/new/container/step-2")

        elif self.request.id == "step-2":
            if not "c_name" in self.request.session:
                self.request.session.push_alert("Missing vital info (Please fill out a name for the container before procceding to step 2)!", level="error")
                return Redirect("/new/container/step-1")

            domain = self.request.getParam("hostname")

            ports = {}
            p = im.Image(self.request.session.c_image).ports
            for port in p:
                ports[port] = self.request.getParam("port_"+port, None)

            container = cm.Container.new_container(user_id=self.request.session.id,
                                                   image_id=self.request.session.c_image,
                                                   name=self.request.session.c_name,
                                                   ports=ports,
                                                   hostname=domain)

            del self.request.session.c_name
            del self.request.session.c_image

            return Redirect("/containers/"+container.id)

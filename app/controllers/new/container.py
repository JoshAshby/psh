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
from rethinkORM import RethinkCollection
from models.utils import dbUtils as dbu

from errors.general import \
      MissingError


@login()
@autoRoute()
class container(MixedObject):
    _title = "New Container - Step 1"
    _default_tmpl = "public/new/container_step_1"
    def GET(self):
        if "c_name" in self.request.session:
            ports = im.Image(self.request.session.c_image)
            self.request.title = "New Container - Step 2"
            self.view.template = "public/new/container_step_2"
            self.view.data = {"ports": ports}
        else:
            q = dbu.rql_where_not(im.Image.table, "disable", True).filter({"user": self.request.session.id})

            q = dbu.rql_highest_revs(q, "dockerfile")

            res = RethinkCollection(im.Image, query=q).fetch()
            self.view.data = {"images": res}

        return self.view

    def POST(self):
        if "c_name" in self.request.session:
            domain = self.request.getParam("domain")
            ports = self.request.getParam("ports")

          # TODO: Process the ports since I highly doubt jquery will serialize
          # it correctly

            container = cm.Container.new_container(
                user=self.request.session.id,
                name=self.request.session.c_name,
                img=self.request.session.c_image,
                ports = ports,
                hostname=domain)

            del self.request.session.c_name
            del self.request.session.c_image

            return Redirect("/containers/"+container.id)
        else:
            name = self.request.getParam("name")
            image = self.request.getParam("image")

            self.request.session.c_image = image
            self.request.session.c_name = name
            

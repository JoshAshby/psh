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
from seshat.actions import Redirect

from models.rethink.image import imageModel as im

from errors.general import \
      MissingError


@login()
@autoRoute()
class index(HTMLObject):
    _title = "New Image"
    _defaultTmpl = "public/new/dockerfile"
    def GET(self):
        return self.view

    def POST(self):
      # TODO: name error handling
        files = self.request.getFile("file")
        name = self.request.getParam("name")
        public = self.request.getParam("public", False)

        try:
            if files:
                image= im.Image.new_image(user_id=self.request.session.id,
                                          name=name,
                                          file_obj=files,
                                          public=public)

            return Redirect("/images/"+image.id)

        except MissingError as e:
            self.view.data = {"name": name, "public": public, "error": str(e)}

            return self.view

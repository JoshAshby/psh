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

import models.redis.announcement.announcementModel as am

from utils.paginate import Paginate

import arrow


@login(["admin"])
@autoRoute()
class index(MixedObject):
    _title = "Site Announcements"
    _default_tmpl = "admin/announcements/index"
    def GET(self):
        announcements = am.all_announcements()

        page = Paginate(announcements, self.request, "created")

        self.view.data = {"page": page, "now": arrow.utcnow().format("MM/DD/YYYY HH:mm")}

        return self.view

    def POST(self):
        status = self.request.getParam("status", False)
        message = self.request.getParam("message")
        start = self.request.getParam("start")
        end = self.request.getParam("end")

        if start:
            start = arrow.get(start, 'MM/DD/YYYY HH:mm').to("UTC").timestamp

        if end:
            end = arrow.get(end, 'MM/DD/YYYY HH:mm').to("UTC").timestamp

        self.request.announcements.new_announcement(message, status, start, end)

        return Redirect("/admin/announcements")

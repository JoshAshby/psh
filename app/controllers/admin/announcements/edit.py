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

import models.redis.baseRedisModel as brm

import arrow


@login(["admin"])
@autoRoute()
class edit(HTMLObject):
    _title = "Site Announcements"
    _defaultTmpl = "admin/announcements/edit"
    def GET(self):
        announcement_id = self.request.id

        announcement = brm.SeshatRedisModel("announcement:"+announcement_id)

        if announcement.start:
            announcement._formated_start = arrow.get(announcement.start).format("MM/DD/YYYY HH:mm")
        if announcement.end:
            announcement._formated_end   = arrow.get(announcement.end).format("MM/DD/YYYY HH:mm")

        self.view.data = {"announcement": announcement, "now": arrow.utcnow().format("MM/DD/YYYY HH:mm")}

        return self.view

    def POST(self):
        ID = self.request.id
        status = self.request.getParam("status", False)
        message = self.request.getParam("message")
        start = self.request.getParam("start")
        end = self.request.getParam("end")

        if start:
            start = arrow.get(start, 'MM/DD/YYYY HH:mm').to("UTC").timestamp

        if end:
            end = arrow.get(end, 'MM/DD/YYYY HH:mm').to("UTC").timestamp

        self.request.announcements.edit_announcement(ID, message, status, start, end)

        self._redirect("/admin/announcements")
        return

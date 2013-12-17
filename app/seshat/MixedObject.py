#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
baseObject to build pages off of

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2012
http://joshashby.com
joshuaashby@joshashby.com
"""
from views.template import template
import json
import traceback
import actions

import base

root_group = "root"


class MixedObject(base.BaseHTTPObject):
    _login = False
    _groups   = []
    _redirect_url = ""
    _type = "HTML"
    def post_init_hook(self):
        self.head = ("200 OK", [("Content-Type", "text/html")])

    def pre_content_hook(self):
        try:
          self.view = template(self._default_tmpl, self.request)
          try:
              title = self._title
          except:
              title = "Untitled"

          self.view.title = title

        except:
          self.view = ""

    def build(self):
        content = ""

        if self._login and not self.request.session.id:
            self.request.session.push_alert("You need to be logged in to view this page.", level="error")
            if not self._redirect_url:
                self.head = ("401 UNAUTHORIZED", [])
            else:
                self.head = ("303 SEE OTHER", [("Location", self._redirect_url)])
            return "", self.head

        if self._groups and (not self.request.session.has_perm(root_group) \
           or not len(set(self._groups).union(self.request.session.groups)) >= 1):
                self.request.session.push_alert("You are not authorized to perfom this action.", level="error")
                if not self._redirect_url:
                    self.head = ("401 UNAUTHORIZED", [])
                else:
                    self.head = ("303 SEE OTHER", [("Location", self._redirect_url)])
                return "", self.head

        self.pre_content_hook()
        try:
            content = getattr(self, self.request.method)()
            if isinstance(content, actions.BaseAction):
                self.head = content.head
            else:
                if not content: content = ""
                content = self.post_content_hook(content)
                if content: content = unicode(content)
        except Exception as e:
            content = (e, traceback.format_exc())

        if self.head[0] not in ["303 SEE OTHER"]:
            del self.request.session.alerts

        return content, self.head

    def post_content_hook(self, content):
        if self._type == "JSON" or type(content) is dict or type(content) is list:
            self.head = (self.head[0], [("Content-Type", "application/json")])

            response = [content]

            return json.dumps(response)

        else:
            self.head = (self.head[0], [("Content-Type", "text/html")])

            if isinstance(content, template):
                string = content.render()
                del content
                return string
            else:
                return content

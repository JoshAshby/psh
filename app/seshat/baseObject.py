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

root_group = "root"


class BaseHTTPObject(object):
        _login = False
        _groups   = []

        """
        Base HTTP page response object
        This determins which REQUEST method to send to,
        along with authentication level needed to access the object.
        """
        def __init__(self, request):
            self.request = request
            self.post_init_hook()

        def post_init_hook(self):
            pass

        def build(self):
            content = ""

            if self._login and not self.request.session.id:
                self.request.session.push_alert("You need to be logged in to view this page.", level="error")
                self._redirect(self._redirect_URL)
                return "", self.head

            if self._groups and (not self.request.session.has_perm(root_group) \
               or not len(set(self._groups).union(self.request.session.groups)) >= 1):
                    self.request.session.push_alert("You are not authorized to perfom this action.", "error")
                    self._redirect(self._redirect_URL)
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

        def pre_content_hook(self):
            pass

        def post_content_hook(self, content):
            return content

        def _404(self):
            self.head = ("404 NOT FOUND", [])

        def _redirect(self, loc):
            self.head = ("303 SEE OTHER", [("Location", loc)])

        def HEAD(self):
            """
            This is wrong since it should only return the headers... technically...
            """
            return self.GET()

        def GET(self):
            pass

        def POST(self):
            pass

        def PUT(self):
            pass

        def DELETE(self):
            pass


class HTMLObject(BaseHTTPObject):
    def post_init_hook(self):
        self.head = ("200 OK", [("Content-Type", "text/html")])

        try:
            title = self._title
        except:
            title = "untitled"

        self.request.title = title

    def pre_content_hook(self):
        try:
          tmpl = self._defaultTmpl
          self.view = template(tmpl, self.request)
        except:
          self.view = ""

    def post_content_hook(self, content):
        if isinstance(content, template):
            string = content.render()
            del content
            return string
        else:
            return content


class JSONObject(BaseHTTPObject):
    def post_init_hook(self):
        self.head = ("200 OK", [("Content-Type", "application/json")])

    def post_content_hook(self, content):
        response = [{"status": self.head[0], "data": content}]

        return json.dumps(response)


class MixedObject(BaseHTTPObject):
    def pre_content_hook(self):
        try:
          self.view = template(self._default_tmpl, self.request)
        except:
          self.view = ""

    def post_content_hook(self, content):
        if self._type == "JSON":
            if not self.head:
                self.head = ("200 OK", [("Content-Type", "application/json")])
            response = [{"data": content}]

            return json.dumps(response)

        elif self._type == "HTML":
            if not self.head:
                self.head = ("200 OK", [("Content-Type", "text/html")])
            if isinstance(content, template):
                string = content.render()
                del content
                return string
            else:
                return content

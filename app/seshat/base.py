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

    def pre_content_hook(self):
        pass

    def build(self):
      content = ""
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

      return content, self.head

    def post_content_hook(self, content):
        return content

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


class MixedObject(BaseHTTPObject):
    _login = False
    _groups   = []
    _redirect_url = ""
    _type = "HTML"
    def post_init_hook(self):
        self.head = ("200 OK", [("Content-Type", "text/html")])

        try:
            title = self._title
        except:
            title = "Untitled"

        self.request.title = title

    def pre_content_hook(self):
        try:
          self.view = template(self._default_tmpl, self.request)
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
        if self._type == "JSON":
            self.head = (self.head[0], [("Content-Type", "application/json")])

            response = [{"data": content}]

            return json.dumps(response)

        elif self._type == "HTML":
            self.head = (self.head[0], [("Content-Type", "text/html")])

            if isinstance(content, template):
                string = content.render()
                del content
                return string
            else:
                return content

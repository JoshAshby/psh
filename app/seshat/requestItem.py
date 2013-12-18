#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
Main framework app

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import logging
logger = logging.getLogger("seshat.request")

import Cookie
import uuid
import cgi
import tempfile
import urlparse

import models.redis.session.sessionModel as sm
import models.redis.bucket.bucketModel as bm
import models.redis.announcement.announcementModel as am


class FileObject(object):
    _template = "< FileObject @ {id} Filename: {filename} Data: {data} >"
    def __init__(self, file_obj):
        self.filename = file_obj.filename
        self.name = file_obj.name
        self.type = file_obj.type
        self.expanded_type = self.type.split("/")
        self.file = file_obj.file

        self.extension = ""
        parts = self.filename.split(".", 1)
        if len(parts) > 1:
            self.extension = parts[1]

    def read(self):
        return self.file.read()

    def readline(self):
        return self.file.readline()

    def seek(self, where):
        return self.file.seek(where)

    def readlines(self):
        return self.file.readlines()

    def auto_read(self):
        self.seek(0)
        data = self.read()
        self.seek(0)
        return data

    def __repr__(self):
      string = self._template.format(**{
          "id": id(self),
          "filename": self.filename,
          "data": len(self.auto_read())
        })
      return string


class requestItem(object):
    def __init__(self, env):
        self.params = {}
        self.files = {}
        self._env = env

        self.url = urlparse.urlparse(env["PATH_INFO"])

        self.buildParams()
        self.buildCookie()
        self.buildSession()
        self.buildCfg()

        self.method = self._env["REQUEST_METHOD"]
        self.remote = env["HTTP_X_REAL_IP"] if "HTTP_X_REAL_IP" in env else "Unknown IP"
        self.user_agent = env["HTTP_USER_AGENT"] if "HTTP_USER_AGENT" in env else "Unknown User Agent"
        self.referer = env["HTTP_REFERER"] if "HTTP_REFERER" in env else "No Referer"

        self.pre_id_url = None
        self.id = None
        self.command = None

    def post_route(self, extended):
        if extended:
            parts = extended.split('/', 1)
            self.id = parts[0]
            if len(parts) > 1:
                self.command = parts[1]
            else:
                self.command = None

        if self.id:
            self.pre_id_url = self.url.path.split(self.id)[0].strip("/").split("/")
        else:
            self.pre_id_url = self.url.path.strip("/").split("/")

    def buildParams(self):
        all_mem = {}
        all_raw = {}
        all_files = {}

        temp_file = tempfile.TemporaryFile()
        temp_file.write(self._env['wsgi.input'].read()) # or use buffered read()
        temp_file.seek(0)
        form = cgi.FieldStorage(fp=temp_file, environ=self._env, keep_blank_values=True)

        for bit in form:
            if hasattr(form[bit], "filename") and form[bit].filename is not None:
                fi = FileObject(form[bit])
                all_files[fi.name] = fi
            else:
                all_mem[bit] = form.getvalue(bit)
                all_raw[bit] = form.getvalue(bit)

        temp_file.close()

        self.params = all_mem
        self.files = all_files

    def buildCookie(self):
        cookie = Cookie.SimpleCookie()
        try:
            cookie.load(self._env["HTTP_COOKIE"])
            self.sessionCookie = { value.key: value.value for key, value in cookie.iteritems() }
            self.sessionID = self.sessionCookie["bug_sid"]
        except:
            self.sessionID = str(uuid.uuid4())
            self.sessionCookie = {"bug_sid": self.sessionID}

    def buildSession(self):
        self.session = sm.session("session:"+self.sessionID)

    def buildCfg(self):
        self.buckets = bm.CfgBuckets()
        self.announcements = am.CfgAnnouncements()

        self.has_announcements = (len(self.announcements._data)>=1)

    def generateHeader(self, header, length):
        for morsal in self.sessionCookie:
            cookieHeader = ("Set-Cookie", ("%s=%s")%(morsal, self.sessionCookie[morsal]))
            header.append(cookieHeader)

        header.append(("Content-Length", str(length)))
        header.append(("Server", self._env["SERVER_SOFTWARE"]))
        header.append(("X-Seshat-Says", "Ello!"))
        if hasattr(self, "error"): header.append(("X-Error", str(self.error)))

        return header

    def getParam(self, param, default="", cast=str):
        try:
            p = self.params[param]
            if cast and cast != str:
                p = cast(p)
            else:
                if p == "True" or p == "true":
                    p = True
                elif p == "False" or p == "false":
                    p = False
            return p
        except:
            return default

    def getFile(self, name):
        if name in self.files and self.files[name].filename:
              return self.files[name]

    @property
    def id_extended(self):
        if self.command is None:
            return str(self.id)
        else:
            return "/".join([self.id, self.command])

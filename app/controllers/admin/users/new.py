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

from models.rethink.user import userModel as um

from errors import user as ue


@login(["admin"])
@autoRoute()
class new(MixedObject):
    _title = "New User"
    _default_tmpl = "admin/users/new"
    def GET(self):
        return self.view

    def POST(self):
        username = self.request.getParam("username")
        password = self.request.getParam("password")
        email = self.request.getParam("email")
        disable = self.request.getParam("disable", False)

        try:
            user = um.User.new_user(username, password, email)

        except ue.UsernameError as e:
            self.view.data = {
                "email": email,
                "password": password,
                "disable": disable,
                "error": "username",
                "error_msg": str(e).strip("'")
                }

            return self.view

        except ue.PasswordError as e:
            self.view.data = {
                "email": email,
                "username": username,
                "disable": disable,
                "error": "password",
                "error_msg": str(e).strip("'")
                }

            return self.view

        except ue.EmailError as e:
            self.view.data = {
                "username": username,
                "password": password,
                "disable": disable,
                "error": "email",
                "error_msg": str(e).strip("'")
                }

            return self.view

        self.request.session.push_alert("User created...", level="success")
        return Redirect("/admin/users/"+user.id)

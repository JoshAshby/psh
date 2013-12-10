#!/usr/bin/env python2
"""
Controller for authentication logout

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from seshat.route import autoRoute
from seshat.baseObject import HTMLObject


@autoRoute()
class logout(HTMLObject):
    def GET(self):
        """
        Simply log the user out. Nothing much to do here.

        redirect to login page after we're done.
        """
        if self.request.session.logout():
            self.request.session.push_alert("Come back soon!",
                                           "B'ahBye...", "info")

        self.head = ("303 SEE OTHER", [("location", ("/login"))])



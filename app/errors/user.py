#!/usr/bin/env python
"""
user model exceptions

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""


class UserModelError(Exception):
    """
    Base exception for the user model

    :param msg: The message that should be passed along in the exception
    """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
    def __unicode__(self):
        return repr(self.msg.decode('utf-8'))


class MultipleUsersError(UserModelError):
    """
    If there are multiple users returned by a search then we want
    to raise this and give the value, whether it was a username or an
    email that caused it, in case we want to know what the exact issue was

    :param msg: The error message
    :param usernameOrEmail: The value which caused multiple users to be returned
        Should be an email or username
    """
    def __init__(self, msg, usernameOrEmail):
        UserModelError.__init__(self, msg)
        self.usernameOrEmail = usernameOrEmail


class PasswordError(UserModelError):
    def __init__(self, msg):
        UserModelError.__init__(self, msg)


class UsernameError(UserModelError):
    def __init__(self, msg, user):
        UserModelError.__init__(self, msg)
        self.user = user


class EmailError(UserModelError):
    def __init__(self, msg, user):
        UserModelError.__init__(self, msg)
        self.email = user

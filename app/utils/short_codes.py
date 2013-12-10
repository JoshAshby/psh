#!/usr/bin/env python
"""
Generate various style of short codes

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import string
import random


def rand_short_code(length=10):
    """
    Its simple: No, we don't kill the batman. We generate random code.
    Return a random selection of alphanumeric symbols. Not guaranteed to be
    unique in any case.
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(length))

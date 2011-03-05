#!/usr/bin/env python

import hashlib

def md5(key):
    """MD5 sum.

    @param key md5 key
    """
    return hashlib.md5(key).hexdigest()

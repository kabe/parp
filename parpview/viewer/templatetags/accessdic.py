#!/usr/bin/env python

from django import template

register = template.Library()


def accessdic(obj, index):
    return obj[index]

register.filter('accessdic', accessdic)

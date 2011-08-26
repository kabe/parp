#!/usr/bin/env python

from django import template

register = template.Library()


def accessdic(obj, index):
    return obj[index]

register.filter('accessdic', accessdic)

def safe_accessdic(obj, index):
    try:
        return obj[index]
    except:
        return ""

register.filter('safe_accessdic', safe_accessdic)

def accessprop(obj, prop):
    try:
        return getattr(obj, prop)
    except:
        return ""

register.filter('accessprop', accessprop)

def remove_func_paren(obj):
    try:
        return obj.replace("()", "")
    except:
        return obj

register.filter('remove_func_paren', remove_func_paren)


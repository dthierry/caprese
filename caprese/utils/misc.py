# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

__author__ = 'David Thierry @2018'


def getattr_rec(obj, attr):
    l_attr = attr.split('.')
    loc_obj = obj
    while l_attr:
        i = l_attr.pop(0)
        loc_obj = getattr(loc_obj, i)
    return loc_obj

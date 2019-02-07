# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from pyomo.core.base import Var
from pyomo.dae.diffvar import DerivativeVar

__author__ = 'David Thierry @2018'


def getattr_rec(obj, attr):
    l_attr = attr.split('.')
    loc_obj = obj
    while l_attr:
        i = l_attr.pop(0)
        loc_obj = getattr(loc_obj, i)
    return loc_obj


def infer_diff_states(model):
    l_ds = []
    for i in model.component_objects(Var):
        if isinstance(i, DerivativeVar):
            l_ds.append(i.name)
    return l_ds

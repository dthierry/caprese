# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from pyomo.core.base import Var
from pyomo.dae.diffvar import DerivativeVar
from caprese.utils.categorize import categorize_variables
from caprese.utils.misc import getattr_rec

__author__ = 'David Thierry @2019'


class AlgorithmBase(object):
    def __init__(self, mod_fun=None, pyomo_mod=None):
        self._mod_class_flag = False
        self._pyomo_mod = False

        if not mod_fun is None:  #: identify model source
            self._mod_class_flag = True
            self._mod_class = mod_fun
        if not pyomo_mod is None:
            self._pyomo_mod = True

        self._ss = None  #: steady state

        self._lstate = []
        self._l_dif_state = []
        self._l_alg_state = []
        self._l_measurement = []
        self._l_input = []

    def _identify_model_src(self):
        pass

    def _generate_steady_state_mod(self):
        m = self._mod_class()
        for i in m.component_objects(Var):
            if isinstance(i, DerivativeVar):
                de = getattr_rec(m, i.name + '_disc_eq')
                print(i.name, len(i), de.name, len(de))
                for item in i.itervalues():
                    item.fix(0.0)
                de.parent_block().del_component(de)  #: for safety
                de.pprint()

        return m

    def _categorize_variables(self, model, time_set_name):
        time_set = getattr_rec(model, time_set_name)
        _n, _t = categorize_variables(model, time_set)

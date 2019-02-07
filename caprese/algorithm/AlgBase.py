# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from pyomo.core.base import Var
from pyomo.dae.diffvar import DerivativeVar
from caprese.utils.categorize import categorize_variables
from caprese.utils.misc import getattr_rec

__author__ = 'David Thierry @2019'


class AlgorithmBase(object):
    def __init__(self, mod_fun=None, pyomo_mod=None, nlp_solver="ipopt"):
        self._mod_class_flag = False
        self._pyomo_mod = False

        if not mod_fun is None:  #: identify model source
            self._mod_class_flag = True
            self._mod_class = mod_fun
        if not pyomo_mod is None:
            self._pyomo_mod = True

        self._nlp_mod = None  #: main model?

        self._l_state = []
        self._l_dif_state = []
        self._l_alg_state = []
        self._l_measurement = []
        self._l_input = []
        self._nlp_solver_base = None

    def _identify_model_src(self):
        pass

    def _pre_process_dae_pyomo(self):
        pass

    def _generate_steady_state_mod(self):
        pass

    def _generate_main_model(self):
        pass

    def _categorize_variables(self, model, time_set_name):
        time_set = getattr_rec(model, time_set_name)
        _n, _t = categorize_variables(model, time_set)

    def get_current_dstate(self):
        pass

    def set_init_dstate(self):
        pass

    def get_current_input(self):
        pass

    def load_mod_var_vals(self):
        pass

    def _assign_solver(self):
        pass

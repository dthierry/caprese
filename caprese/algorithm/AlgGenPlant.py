# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from pyomo.core.base import Var
from pyomo.dae.diffvar import DerivativeVar
from caprese.algorithm.AlgBase import AlgorithmBase
from caprese.utils.categorize import categorize_variables
from caprese.utils.misc import getattr_rec
from pyomo.opt import SolverFactory, SolverStatus

__author__ = 'David Thierry @2018'


class GenDynP(AlgorithmBase):
    def __init__(self, mod_fun=None, pyomo_mod=None, solver="ipopt"):
        super(AlgorithmBase, GenDynP).__init__(mod_fun=mod_fun, pyomo_mod=pyomo_mod)
        self._steady_state = self._generate_steady_state_mod()
        self._nlp_solver_base = SolverFactory(solver)

    def _generate_steady_state_mod(self):
        m = self._mod_class()
        for i in m.component_objects(Var):
            if isinstance(i, DerivativeVar):
                de = getattr_rec(m, i.name + '_disc_eq')
                for item in i.itervalues():
                    item.fix(0.0)
                de.parent_block().del_component(de)  #: for safety
        return m

    def _init_from_ss(self, solve=True):
        r = self._nlp_solver_base.solve(self._steady_state, tee=True)
        if r.solver.status != SolverStatus.ok:
            raise Exception


class SingleDynP(GenDynP):
    def __init__(self):
        super(GenDynP, SingleDynP).__init__()
        self._mod = self._generate_main_model()

    def _generate_main_model(self):
        m = self._mod_class(nfe=1, ncp=1)
        return m


class SimulatedMismatchedDynP(GenDynP):
    def __init__(self):
        super(GenDynP, SimulatedMismatchedDynP).__init__()

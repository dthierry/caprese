# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

from pyomo.core.base import Block, Var, Reference
from pyomo.core.base.block import SubclassOf
from pyomo.core.base.sets import _SetProduct
from pyomo.core.base.indexed_component_slice import _IndexedComponent_slice


def identify_member_sets(index):
    if index is None:
        return []
    queue = [index]
    ans = []
    while queue:
        s = queue.pop(0)
        if not isinstance(s, _SetProduct):
            ans.append(s)
        else:
            queue.extend(s.set_tuple)
    return ans


def generate_time_only_slices(obj, time):
    o_sets = identify_member_sets(obj.index_set())
    # Given a potentially complex set, determine the index of the TIME
    # set, as well as all other "fixed" indices.  We will even support a
    # single Set with dimen==None (using ellipsis in the slice).
    ellipsis_idx = None
    time_idx = None
    regular_idx = []
    idx = 0
    for s in o_sets:
        if s is time:
            time_idx = idx
            idx += 1
        elif s.dimen is not None:
            for sub_idx in range(s.dimen):
                regular_idx.append(idx)
            idx += s.dimen
        elif ellipsis_idx is None:
            ellipsis_idx = idx
            idx += 1
        else:
            raise RuntimeError(
                "We can only handle a single Set with dimen=None")
    # To support Sets with dimen==None (using ellipsis), we need to have
    # all fixed/time indices be positive if they appear before the
    # ellipsis and negative (counting from the end of the list) if they
    # are after the ellipsis.
    if ellipsis_idx:
        if time_idx > ellipsis_idx:
            time_idx = time_idx - idx
        regular_idx = [i - idx if i > ellipsis_idx else i
                       for i in fixed_idx]  #: fixme
    # We now form a temporary slice that slices over all the regular
    # indices for a fixed value of the time index.
    tmp_sliced = {i: slice(None) for i in regular_idx}
    tmp_fixed = {time_idx: time.first()}
    tmp_ellipsis = ellipsis_idx
    _slice = _IndexedComponent_slice(
        obj, tmp_fixed, tmp_sliced, tmp_ellipsis
    )
    # For each combination of regular indices, we can generate a single
    # slice over the time index
    time_sliced = {time_idx: time.first()}
    for key in _slice.wildcard_keys():
        if type(key) is not tuple:
            key = (key,)
        time_fixed = dict(
            (i, val) if i < time_idx else (i + 1, val)
            for i, val in enumerate(key)
        )
        yield _IndexedComponent_slice(obj, time_fixed, time_sliced, None)


def generate_time_indexed_block_slices(block, time):
    # TODO: We should probably do a sanity check that time does not
    # appeat in any sub-block / var indices.
    queue = list(generate_time_only_slices(block, time))
    while queue:
        _slice = queue.pop(0)
        # Pick a random block from this slice (i.e. TIME == TIME.first())
        #
        # TODO: we should probably sometime check that the OTHER blocks
        # in the time set have the same variables.
        b = next(iter(_slice))
        # Any sub-blocks must be put on the queue to descend into and
        # process
        for sub_b in b.component_objects(Block, descend_into=False):
            _name = sub_b.local_name
            for idx in sub_b:
                queue.append(_slice.duplicate().component(_name)[idx])
        # Any Vars must be mapped to slices and returned
        for v in b.component_objects(Var, descend_into=False):
            _name = v.local_name
            for idx in v:
                yield _slice.duplicate().component(_name)[idx]


def categorize_variables(model, time):
    assert time.model() is model.model()

    block_queue = [model]
    regular_vars = []
    time_indexed_vars = []
    while block_queue:
        b = block_queue.pop(0)
        b_sets = identify_member_sets(b.index_set())
        if time in b_sets:
            for _slice in generate_time_indexed_block_slices(b, time):
                time_indexed_vars.append(Reference(_slice))
            continue
        block_queue.extend(
            list(b.component_objects(Block, descend_into=False))
        )
        for v in b.component_objects(SubclassOf(Var), descend_into=False):
            v_sets = identify_member_sets(v.index_set())
            if time in v_sets:
                for _slice in generate_time_only_slices(v, time):
                    time_indexed_vars.append(Reference(_slice))
            else:
                regular_vars.extend(list(v.values()))

    return regular_vars, time_indexed_vars

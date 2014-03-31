""" ixle.heuristics.util
"""

from ixle.util import get_heuristics
from .base import DirHeuristic

def run_heuristic(hname, item):
    h = get_heuristics()[hname](item)
    return {h:h()}

def run_dir_heuristics(item):

    results = {}
    for fxn_name, H in get_heuristics().items():
        if H==DirHeuristic or not issubclass(H, DirHeuristic):
            continue
        else:
            results.update(run_heuristic(fxn_name, item))
    return results

def get_dir_suggestions(item):
    stuff = run_dir_heuristics(item)
    out = {}
    for hobj, hnswer in stuff.items():
        if getattr(hobj, 'suggestion', None) and hnswer:
            out[hobj] = hnswer
    return out

def run_heuristics(item):
    results = {}
    for fxn_name, fxn in get_heuristics().items():
        results.update(run_heuristic(fxn_name,item))
    return results

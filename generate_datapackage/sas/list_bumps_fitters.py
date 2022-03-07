#!/usr/bin/env python

import bumps.fitters

from pprint import pprint


class_list = dir(bumps.fitters)

def is_fitter(name):
    if name != "FitBase" and name != "FitDriver":
        return "Fit" in name
    return False
fitter_list = list(filter(is_fitter, class_list))

fitter_dict = { fitter: getattr(bumps.fitters, fitter).id for fitter in fitter_list }

pprint(fitter_dict)

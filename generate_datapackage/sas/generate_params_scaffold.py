#!/usr/bin/env python

import os
import sys
import json

SASVIEW_SOURCE_PATH = os.environ.get("SASVIEW_SOURCE")
sys.path.append(SASVIEW_SOURCE_PATH)

import sasmodels as sm
from sasmodels.sasview_model import load_standard_models 
from sasmodels.weights import MODELS as POLYDISPERSITY_MODELS

from helpers import make_human_readable


SCAFFOLD_DIR = "./algorithms/sas/inputs/"


# =============================================================================
# Helpers


def diff(list1, list2):
    # Returns difference between two lists
    return list(set(list1) - set(list2))


def index(lst, key, value):
    # Find index of item matching i[key] == value in a list of dicts
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None


# =============================================================================
# SasView model conversion helpers


def _base_sasview_model_to_view_spec(model, title_prefix=""):
    params = diff(model.getParamList(), model.getDispParamList())

    # Make view descriptor
    view_descriptor = {
        "name": model.name + "_view",
        # "title": title_prefix + " (" + make_human_readable(model.name) + ")",
        "title": title_prefix,
        "resources": [model.name],
        "specType": "opendatafit-params",
        "spec": {
            "keys": [],
        },
    }

    for param in params:
        # No orientation params in 1D
        if param not in model.orientation_params:
            # Append parameter metadata
            view_descriptor["spec"]["keys"].append(
                {
                    "name": param,
                }
            )

    return view_descriptor


def sasview_model_to_view_spec(model, polydispersity=False, title_prefix=""):
    # Build base params view
    view_descriptor = _base_sasview_model_to_view_spec(
        model,
        title_prefix=title_prefix
    )

    if not polydispersity:
        return view_descriptor

    # Dispersion parameters
    for param in model.dispersion.keys():
        # No orientation params in 1D
        # Exclude magnetic parameters
        if (
            param not in model.orientation_params
            and param not in model.magnetic_params
        ):
            param_pd = param + "_pd"
            param_pd_n = param + "_pd_n"
            param_pd_nsigma = param + "_pd_nsigma"
            param_pd_type = param + "_pd_type"

            # Append polydispersity sub-parameters to view
            ind = index(view_descriptor["spec"]["keys"], "name", param)
            view_descriptor["spec"]["keys"][ind].update(
                {
                    "keys": [
                        {
                            "name": param_pd,
                        },
                        {
                            "name": param_pd_n,
                        },
                        {
                            "name": param_pd_nsigma,
                        },
                        {
                            "name": param_pd_type,
                        },
                    ],
                }
            )

    return view_descriptor


def _base_sasview_model_to_parameter_resource(model):
    # Build resource containing a list of available parameters for a given
    # sasmodel
    params = diff(model.getParamList(), model.getDispParamList())

    # Data resource
    data = {}
    keys = []

    for param in params:
        # No orientation params in 1D
        if param not in model.orientation_params:
            # Populate in case defaults are empty
            # [0]: Units, [1]: Min, [2]: Max
            if param not in model.details:
                model.details[param] = ["", None, None]

            value = model.getParam(param)  # Default value
            lower = model.details[param][1]
            upper = model.details[param][2]
            unit = model.details[param][0]

            # If not fittable still acts as fixed variable but should not be
            # able to be selected for fitting
            fittable = param not in model.non_fittable

            # Default all parameters to fixed/non-variable
            vary = False

            keys.append(
                {
                    "name": param,
                    "unit": unit,
                    "fields": [
                        {
                            "name": "vary",
                            "title": "Vary",
                            "type": "boolean",
                        },
                        {
                            "name": "value",
                            "title": "Value",
                            "type": "number",
                        },
                        {
                            "name": "lowerBound",
                            "group": "constraints",
                            "title": "Lower bound",
                            "type": "number",
                        },
                        {
                            "name": "upperBound",
                            "group": "constraints",
                            "title": "Upper bound",
                            "type": "number",
                        },
                        # {
                        #    "name": "fittable",
                        #    "title": "Fittable",
                        #    "type": "boolean",
                        # },
                    ],
                }
            )

            data[param] = {
                "vary": vary,
                "value": value,
                "lowerBound": lower,
                "upperBound": upper,
                # "fittable": fittable,
            }

    resource = {
        "name": model.name,
        "format": "json",
        "scheme": "memory",
        "data": data,
        "schema": {
            "fields": [],  # Temporarily squash schema validation error
            "keys": keys,
        },
        # TODO: Profile ID must be a URL that points to JSON schema to validate
        # profile
        # TODO: Temporary workaround for profile validation
        "profile": "data-resource",
        "tmpprofile": "parameter-data-resource",
    }

    # TODO: Temporary workaround for profile validation
    resource["tmpprofile"] = "parameter-data-resource"

    return resource


def sasview_model_to_parameter_resource(model, polydispersity=False):
    # Build base params resource
    resource = _base_sasview_model_to_parameter_resource(model)

    # Return only base model params if polydispersity disabled
    if not polydispersity:
        return resource

    # Polydispersity type options enum
    # Default: gaussian
    pd_types = [name for name in POLYDISPERSITY_MODELS.keys()]

    # Add polydispersity group definition
    resource["schema"]["groups"] = [
        {
            "name": "polydispersity",
            "title": "Polydispersity",
        }
    ]

    # Dispersion parameters
    for param in model.dispersion.keys():
        # No orientation params in 1D
        # Exclude magnetic parameters
        if (
            param not in model.orientation_params
            and param not in model.magnetic_params
        ):
            # To reference individual param in bumps:
            # param + key (width/npts/nsigma/type)
            disp = model.dispersion[param]

            width = disp["width"]
            width_key = param + ".width"
            width_lower = model.details[width_key][1]
            width_upper = model.details[width_key][2]
            width_unit = model.details[width_key][0]

            npts = disp["npts"]
            nsigma = disp["nsigmas"]
            pd_type = disp["type"]

            vary = False  # default

            # Set param names
            param_pd = param + "_pd"
            param_pd_n = param + "_pd_n"
            param_pd_nsigma = param + "_pd_nsigma"
            param_pd_type = param + "_pd_type"

            # Append polydispersity parameter metadata to parent key fields
            resource["schema"]["keys"].extend(
                [
                    {
                        "name": param_pd,
                        "title": "Width",
                        "description": "Polydispersity width of parameter:"
                        + param,
                        "unit": width_unit,
                        "groups": ["polydispersity"],
                        "fields": [
                            {
                                "name": "vary",
                                "title": "Vary",
                                "type": "boolean",
                            },
                            {
                                "name": "value",
                                "title": "Value",
                                "type": "integer",
                                "constraints": {
                                    "min": 0,
                                },
                            },
                            {
                                "name": "lowerBound",
                                "title": "Lower bound",
                                "type": "number",
                            },
                            {
                                "name": "upperBound",
                                "title": "Upper bound",
                                "type": "number",
                            },
                            # {
                            #    "name": "fittable",
                            #    "title": "Fittable",
                            #    "type": "boolean",
                            # },
                        ],
                    },
                    {
                        "name": param_pd_n,
                        "title": "N points",
                        "description": "Number of points",
                        "groups": ["polydispersity"],
                        "fields": [
                            {
                                "name": "value",
                                "title": "Value",
                                "type": "integer",
                                "constraints": {
                                    "min": 0,
                                },
                            },
                        ],
                    },
                    {
                        "name": param_pd_nsigma,
                        "title": "N sigmas",
                        "groups": ["polydispersity"],
                        "fields": [
                            {
                                "name": "value",
                                "title": "Value",
                                "type": "number",
                            },
                        ],
                    },
                    {
                        "name": param_pd_type,
                        "title": "Type",
                        "description": "Polydispersity type",
                        "groups": ["polydispersity"],
                        "fields": [
                            {
                                "name": "value",
                                "title": "Value",
                                "type": "string",
                                "constraints": {
                                    "enum": pd_types,
                                },
                            },
                        ],
                    },
                ]
            )

            # Add polydispersity parameter values
            resource["data"].update(
                {
                    param_pd: {
                        "value": width,
                        "lowerBound": width_lower,
                        "upperBound": width_upper,
                        # "fittable": True,
                        "vary": vary,
                    },
                    param_pd_n: {
                        "value": npts,
                    },
                    param_pd_nsigma: {
                        "value": nsigma,
                    },
                    param_pd_type: {
                        "value": pd_type,
                    },
                }
            )

            # Add polydispersity parameters to relatedKeys on parent param if
            # found

            # Get index of parent param in keys list
            ind = index(resource["schema"]["keys"], "name", param)

            if ind is not None:
                resource["schema"]["keys"][ind].update(
                    {
                        "relatedKeys": [
                            param_pd,
                            param_pd_n,
                            param_pd_nsigma,
                            param_pd_type,
                        ]
                    }
                )

    return resource


# =============================================================================
# Generate resources


if __name__ == "__main__":
    params_resources = []
    params_views = []

    sf_params_resources =[]
    sf_params_views =[]

    # Load all available sasmodels (as SasviewModel classes)
    # SasviewModel - apparently a sasview wrapper for kernel model used in bumps
    # These are *somehow* converted into bumps models through a convoluted network
    # of classes incl. SasFitness, FitProblem, BumpsFit
    # See:
    # sascalc/fit/BumpsFitting.py
    # perspectives/fitting/fitting.py
    # perspectives/fitting/fitproblem.py
    # perspectives/fitting/fitstate.py

    for model in load_standard_models():
        if not model.is_structure_factor:
            resource = sasview_model_to_parameter_resource(
                model(),
                polydispersity=True,
            )

            view = sasview_model_to_view_spec(
                model(),
                polydispersity=True,
                title_prefix="Model parameters",
            )

            params_resources.append(resource)
            params_views.append(view)
        else:
            resource = sasview_model_to_parameter_resource(
                model(),
                polydispersity=False,
            )

            view = sasview_model_to_view_spec(
                model(),
                polydispersity=False,
                title_prefix="Structure factor model parameters",
            )

            sf_params_resources.append(resource)
            sf_params_views.append(view)

    params_output = {
        "resourceScaffolds": params_resources,
        "viewScaffolds": params_views,
    }

    sf_params_output = {
        "resourceScaffolds": sf_params_resources,
        "viewScaffolds": sf_params_views,
    }

    params_json = json.dumps(params_output, indent=2)
    params_json = params_json.replace(": Infinity", ': "Infinity"').replace(
        ": -Infinity", ': "-Infinity"'
    )

    sf_params_json = json.dumps(sf_params_output, indent=2)
    sf_params_json = sf_params_json.replace(": Infinity", ': "Infinity"').replace(
        ": -Infinity", ': "-Infinity"'
    )

    with open(SCAFFOLD_DIR+"params.json", "w") as f:
        f.write(params_json)

    with open(SCAFFOLD_DIR+"sf_params.json", "w") as f:
        f.write(sf_params_json)

    print("Done!")


# TODO: How is a param set to be fitted? see self.select_param
# -> self._manager.set_param2fit (param2fit list)

# TODO: IMPLEMENT LATER:
# MAGNETISM TAB
# See lines 2994-3147 of sasview fitting/fitpage.py

# FIT OPTIONS:
# Min global range
# Max global range
# Npts
# Npts (Fit) - log spaced points
# Weighting
# Smearing
# Npts : self.Npts_fit, self.Npts_total, self.npts_x
# min/max = qmin, qmax - units A^-1

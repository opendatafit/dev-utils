#!/usr/bin/env python

import os
import sys
import json

SASVIEW_SOURCE_PATH = os.environ.get("SASVIEW_SOURCE")
sys.path.append(SASVIEW_SOURCE_PATH)

import sasmodels as sm
from sasmodels.sasview_model import load_standard_models 


SCAFFOLD_DIR = "./algorithms/sas/inputs/"

DEFAULT_MODEL = "sphere"
DEFAULT_SF_MODEL = "hayter_msa"


# Available methods for fitting
# See: list_bumps_fitters.py

methods = [
    {
        "title": "Levenberg-Marquardt",
        "name": "LevenbergMarquardtFit"
    },
    {
        "title": "BFGS",
        "name": "BFGSFit"
    },
    {
        "title": "Simplex",
        "name": "SimplexFit"
    }
]


# Generate model enum options

# Load all available sasmodels
model_dict = { model.name: model for model in load_standard_models() }

models = []
sf_models = []

for model in model_dict.values():
    if model.is_structure_factor:
        sf_models.append({
            "title": model.name,
            "name": model.name,
        })
    else:
        # Enable/disable structure factor selection
        # Based on sasview logic in perspectives/fitting/basepage.py:2026
        if not hasattr(model, "is_form_factor") or not model.is_form_factor:
            sf = False
        else:
            sf = True

        models.append({
            "title": model.name, # Human readable name
            "name": model.name, # Model key
            "category": model.category, # List category
            "structureFactor": sf, # Enable/disable structure factor selection
        })

# Add "None" option for structure factor
sf_models.append({
    "title": "None",
    "name": "",
})

fields = [
    {
        "name": "method",
        "title": "Method",
        "description": "The optimisation method to use for fitting",
        "type": "object",
        "objectFields": [
            {
                "name": "title",
                "type": "string",
            },
            {
                "name": "name",
                "type": "string",
            },
        ],
        "constraints": {
            "enum": methods,
        }
    },
    {
        "name": "model",
        "title": "Model",
        "description": "Model to use for fitting",
        "type": "object",
        "objectFields": [
            {
                "name": "title",
                "type": "string",
            },
            {
                "name": "name",
                "type": "string",
            },
            {
                "name": "category",
                "type": "string",
                "description": "Model category",
            },
            {
                "name": "structureFactor",
                "type": "string",
                "description": "Whether structure factor fitting is available for this model",
            },
        ],
        "constraints": {
            "enum": models,
        }
    },
    {
        "name": "structureFactor",
        "title": "Structure factor",
        "description": "Structure factor model to fit",
        "type": "object",
        "objectFields": [
            {
                "name": "title",
                "type": "string",
            },
            {
                "name": "name",
                "type": "string",
            },
        ],
        "constraints": {
            "enum": sf_models,
        }
    },
]


# Default selections
data = {
    "method": methods[0],
    "model": next(i for i in models if i["name"] == DEFAULT_MODEL),
    "structureFactor": next(i for i in sf_models if i["name"] == DEFAULT_SF_MODEL),
}


# Build resource
resource = {
    "name": "sas_options",
    # TODO: Profile ID must be a URL that points to JSON schema to validate
    # profile
    # Essentially just tabular data with only one row allowed, plus extra
    # objectFields description
    # TODO: Temporary workaround for profile validation until json schema
    # developed
    "profile": "data-resource",
    "tmpprofile": "opendatafit-options",
    "format": "json",
    "data": data,
    "schema": {
      "fields": fields,
    }
}

# Define view
view = {
    "name": "sas_options_view",
    "resources": ["sas_options"],
    "specType": "opendatafit-options",
    "spec": {
        "fields": [
            {
                "name": "method",
            },
            {
                "name": "model",
                "behaviours": [
                    {
                        "name": "changeModel",
                        "do": [
                            "replaceResourceWithScaffold('sas', 'params', getResourceFieldValue('sas_options', 'model.name'), 'sas_params');",
                            "replaceViewWithScaffold('sas', 'params', getResourceFieldValue('sas_options', 'model.name') + '_view', 'sas_params_view');",
                            "if (getResourceFieldValue('sas_options', 'model.structureFactor')) {",
                            "  setViewFieldValue('sas_options_view', 'structureFactor', 'disabled', false);",
                            "  setViewValue('sas_sf_params_view', 'disabled', false);",
                            "  replaceViewWithScaffold('sas', 'sf_params', getResourceFieldValue('sas_options', 'structureFactor.name') + '_view', 'sas_sf_params_view');",
                            "} else {",
                            "  setViewFieldValue('sas_options_view', 'structureFactor', 'disabled', true);",
                            "  setViewValue('sas_sf_params_view', 'disabled', true);",
                            "}",
                        ],
                    },
                ],
            },
            {
                "name": "structureFactor",
                "behaviours": [
                    {
                        "name": "changeStructureFactor",
                        "do": [
                            "if (getResourceFieldValue('sas_options', 'structureFactor.name')) {",
                            "  setViewValue('sas_sf_params_view', 'disabled', false);",
                            "  replaceResourceWithScaffold('sas', 'sf_params', getResourceFieldValue('sas_options', 'structureFactor.name'), 'sas_sf_params');",
                            "  replaceViewWithScaffold('sas', 'sf_params', getResourceFieldValue('sas_options', 'structureFactor.name') + '_view', 'sas_sf_params_view');",
                            "} else {",
                            "  setViewValue('sas_sf_params_view', 'disabled', true);",
                            "}",
                        ],
                    },
                ],
            },
        ],
    },
}

output = {
    "resources": [resource],
    "views": [view],
}

output_json = json.dumps(output, indent=2)

with open(SCAFFOLD_DIR+"options.json", "w") as f:
    f.write(output_json)

print("Done!")

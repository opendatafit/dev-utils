#!/usr/bin/env python

import json
import base64
import os
from copy import deepcopy


DEFAULT_MODEL = "sphere"
DEFAULT_SF_MODEL = "hayter_msa"


def find(lst, key, value):
    for i in lst:
        if i[key] == value:
            return i
    return None


with open("sas.template") as f:
    pkg = json.load(f)


for algo in pkg["algorithms"]:
    # Populate code in B64
    with open(
        "algorithms/sas/" + "/" + algo["name"] + ".py", "rb"
    ) as f:
        algo["code"] = base64.b64encode(f.read()).decode("utf-8")

    for i in algo["inputs"]:
        path = "algorithms/sas/inputs/" + i["name"] + ".json"

        if os.path.isfile(path):
            with open(path, "r") as f:
                jsn = json.load(f)

            resources = jsn.get("resources", False)
            resource_scaffolds = jsn.get("resourceScaffolds", False)
            views = jsn.get("views", False)
            view_scaffolds = jsn.get("viewScaffolds", False)

            if resources:
                pkg["resources"].extend(resources)
                default_resource = resources[0]
                i["resource"] = default_resource["name"]

            if resource_scaffolds:
                i["resourceScaffolds"] = resource_scaffolds

                # Set default input resource from scaffold
                i["resource"] = algo["name"]+"_"+i["name"]

                if i["name"] == "params":
                    default_resource = deepcopy(find(
                        resource_scaffolds,
                        "name",
                        DEFAULT_MODEL,
                    ))
                elif i["name"] == "sf_params":
                    default_resource = deepcopy(find(
                        resource_scaffolds,
                        "name",
                        DEFAULT_SF_MODEL,
                    ))

                default_resource["name"] = i["resource"]

                pkg["resources"].append(default_resource)

            if views:
                pkg["views"].extend(views)

            if view_scaffolds:
                i["viewScaffolds"] = view_scaffolds

                scaffold_keys =  [ i["name"] for i in view_scaffolds ]

                if DEFAULT_MODEL+"_view" in scaffold_keys:
                    default_view = deepcopy(find(
                        view_scaffolds,
                        "name",
                        DEFAULT_MODEL+"_view",
                    ))
                elif "hayter_msa_view" in scaffold_keys:
                    default_view = deepcopy(find(
                        view_scaffolds,
                        "name",
                        "hayter_msa_view",
                    ))

                default_view["resources"] = [
                    default_resource["name"],
                ]
                if i["name"] == "params":
                    default_view["resources"].append("sas_result_params")
                if i["name"] == "sf_params":
                    default_view["resources"].append("sas_result_sf_params")

                default_view["name"] = default_resource["name"]+"_view"

                pkg["views"].append(default_view)


    for o in algo["outputs"]:
        path = "algorithms/sas/outputs/" + o["name"] + ".json"

        with open(path, "r") as f:
            jsn = json.load(f)

            views = jsn.get("views")
            resources = jsn.get("resources")

            if views is not None:
                pkg["views"].extend(views)

            if resources is not None:
                pkg["resources"].extend(resources)


with open("./datapackage.json", "w") as f:
    json.dump(pkg, f, indent=2)


print("Done!")

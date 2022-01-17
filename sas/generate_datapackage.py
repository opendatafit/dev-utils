#!/usr/bin/env python

# Import pipeline-template.json
# Populate all algorithm code and Dockerfile fields (in base64)
# Export to text

import json
import base64
import os
from copy import deepcopy


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
        "algorithms/" + "/" + algo["name"] + ".py", "rb"
    ) as f:
        algo["code"] = base64.b64encode(f.read()).decode("utf-8")

    for i in algo["inputs"]:
        path = "algorithms/inputs/" + i["name"] + ".json"

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

                if i.get("behaviours", False):
                    default_resource["behaviours"] = i.pop("behaviours")

                i["resource"] = default_resource["name"]

            if resource_scaffolds:
                i["resourceScaffolds"] = resource_scaffolds

                # Set default input resource from scaffold
                i["resource"] = algo["name"]+"_"+i["name"]

                if i["name"] == "params":
                    default_resource = deepcopy(find(
                        resource_scaffolds,
                        "name",
                        "sphere",
                    ))
                elif i["name"] == "sf_params":
                    default_resource = deepcopy(find(
                        resource_scaffolds,
                        "name",
                        "hayter_msa",
                    ))

                default_resource["name"] = i["resource"]

                if i.get("behaviours", False):
                    default_resource["behaviours"] = i.pop("behaviours")

                pkg["resources"].append(default_resource)

            if views:
                pkg["views"].extend(views)

            if view_scaffolds:
                i["viewScaffolds"] = view_scaffolds

                scaffold_keys =  [i["name"] for i in view_scaffolds ]

                if "sphere_view" in scaffold_keys:
                    default_view = deepcopy(find(
                        view_scaffolds,
                        "name",
                        "sphere_view",
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

                default_view["name"] = default_resource["name"]+"_view"
                pkg["views"].append(default_view)


    for o in algo["outputs"]:
        # Create placeholder empty resource for all outputs with name in
        # "resource" field
        pkg["resources"].append({
            "name": o["resource"],
        })

        path = "algorithms/outputs/" + o["name"] + ".json"

        if os.path.isfile(path):
            with open(path, "r") as f:
                jsn = json.load(f)

                views = jsn.get("views", False)

                if views:
                    # Add all resources to package
                    pkg["views"].extend(views)


with open("./datapackage.json", "w") as f:
    json.dump(pkg, f)


print("Done!")

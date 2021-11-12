#!/usr/bin/env python

# Import pipeline-template.json
# Populate all algorithm code and Dockerfile fields (in base64)
# Export to text

import json
import base64
import os

with open("datapackage-sas.template") as f:
    pkg = json.load(f)

for algo in pkg["algorithms"]:
    # Populate code in B64
    with open(
        "algorithms/" + algo["name"] + "/" + algo["name"] + ".py", "rb"
    ) as f:
        algo["code"] = base64.b64encode(f.read()).decode("utf-8")

    # Populate resources and views for all inputs and outputs
    for i in algo["inputs"]:
        path = "algorithms/" + algo["name"] + "/inputs/" + i["name"] + ".json"

        if os.path.isfile(path):
            with open(path, "r") as f:
                jsn = json.load(f)

                resources = jsn.get("resources", False)
                views = jsn.get("views", False)

                if resources:
                    # Add all resources to package
                    pkg["resources"].extend(resources)
                    # Set default resource for input
                    i["resource"] = resources[0]["name"]
                    # Populate all available resources for input
                    i["resources"] = [ r["name"] for r in resources ]

                if views:
                    # Add all resources to package
                    pkg["views"].extend(views)

    for o in algo["outputs"]:
        # Create placeholder empty resource for all outputs with name in
        # "resource" field
        pkg["resources"].append({
            "name": o["resource"],
        })

        path = "algorithms/" + algo["name"] + "/outputs/" + o["name"] + ".json"

        if os.path.isfile(path):
            with open(path, "r") as f:
                jsn = json.load(f)

                views = jsn.get("views", False)

                if views:
                    # Add all resources to package
                    pkg["views"].extend(views)

with open("./datapackage_sas.json", "w") as f:
    json.dump(pkg, f)

print("Done!")

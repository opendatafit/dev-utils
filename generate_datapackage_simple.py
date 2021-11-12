#!/usr/bin/env python

# Import pipeline-template.json
# Populate all algorithm code and Dockerfile fields (in base64)
# Export to text

import json
import base64

with open("datapackage-simple.template") as f:
    pkg = json.load(f)

for algo in pkg["algorithms"]:
    with open("algorithms/simple/" + algo["name"] + ".py", "rb") as f:
        algo["code"] = base64.b64encode(f.read()).decode("utf-8")

for container in pkg["containers"]:
    with open("containers/simple/" + container["name"] + ".Dockerfile", "rb") as f:
        container["dockerfile"] = base64.b64encode(f.read()).decode("utf-8")

with open("./datapackage_simple.json", "w") as f:
    json.dump(pkg, f)

print("Done!")

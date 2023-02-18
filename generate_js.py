#!/usr/bin/env python3

import argparse
import json

parser = argparse.ArgumentParser()

parser.add_argument("name")
parser.add_argument("datapackage", help = "Input datapackage path")

parser.add_argument("-o", "--output", help = "Output file path")

args = parser.parse_args()

name = args.name
caps_name = name.upper()

if args.output:
    output_file_path = args.output
else:
    output_file_path = f"js/{name}.js"


with open(args.datapackage) as file:
    datapackage_content = file.read()
    datapackage_json = json.loads(datapackage_content)

with open(output_file_path, "w") as file:
    file.truncate(0)
    file.write(f"const {caps_name} = ")
    # file.write(datapackage_content+";")
    json.dump(datapackage_json, file, indent=2)
    file.write(";\n\n")
    file.write(f"export {{ {caps_name} }};")


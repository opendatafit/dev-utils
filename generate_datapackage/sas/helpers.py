# Convenience method for converting model names to human readable titles

def make_human_readable(name):
    exceptions = {
        "hardsphere": "Hard Sphere",
        "stickyhardsphere": "Sticky Hard Sphere",
        "squarewell": "Square Well",
        "hayter_msa": "Hayter MSA",
        "bcc_paracrystal": "BCC Paracrystal",
        "fcc_paracrystal": "FCC Paracrystal",
        "sc_paracrystal": "SC Paracrystal",
        "be_polyelectrolyte": "BE Polyelectrolyte",
        "rpa": "RPA",
        "dab": "DAB",
        "shape-independent": "Shape-independent",
    }

    if name in exceptions:
        return exceptions[name]
    elif "shape:" in name:
        return ": ".join([ i.capitalize() for i in name.split(":") ])
    else:
        return " ".join([ i.capitalize() for i in name.split("_") ])


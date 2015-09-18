import datetime

def generate_info(name, version, depends):
    return {
        "{name}-{version}-0.tar.bz2".format(name=name, version=version): {
            "build": "0",
            "build_number": 0,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "depends": depends,
            "name": name,
            "size": 0,
            "version": str(version)
            }
    }

REPODATA = {
  "info": {
    "arch": "x86_64",
    "platform": "osx"
  },
  "packages": {}
}

def generate_cells():
    packages = {}
    for row in range(1, 10):
        for column in range(1, 10):
            for entry in range(1, 10):
                depends = []
                for d in range(1, 10):
                    if d == entry:
                        continue
                    # Each entry being 1 requires that the other entries be 0
                    depends.append("%sx%s-is-%s 0" % (row, column, d))

                p1 = generate_info("%sx%s-is-%s" % (row, column, entry), 1,
                    depends)
                p0 = generate_info("%sx%s-is-%s" % (row, column, entry), 0, [])
                packages.update({**p0, **p1})

    return packages

print(generate_cells())

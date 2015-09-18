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
                depends1 = []
                depends0 = []
                for d in range(1, 10):
                    if d == entry:
                        continue
                    # Each entry being set (version 1) requires that the other
                    # entries are not set (version 0)
                    depends1.append("%sx%s-is-%s 0" % (row, column, d))

                for other_row in range(1, 10):
                    if other_row == row:
                        continue
                    # If an entry is set, other cells in the same column can't
                    # have the same entry.
                    depends1.append("%sx%s-is-%s 0" % (other_row, column, entry))

                for other_column in range(1, 10):
                    if other_column == column:
                        continue
                    # If an entry is set, other cells in the same row can't
                    # have the same entry.
                    depends1.append("%sx%s-is-%s 0" % (row, other_column, entry))

                p1 = generate_info("%sx%s-is-%s" % (row, column, entry), 1, depends1)
                p0 = generate_info("%sx%s-is-%s" % (row, column, entry), 0, depends0)
                packages.update({**p0, **p1})

    return packages

print(generate_cells())

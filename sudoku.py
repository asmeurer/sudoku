import datetime

REPODATA = {
  "info": {
    "arch": "x86_64",
    "platform": "osx"
  },
  "packages": {}
}

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

def generate_cells():
    packages = {}
    for row in range(1, 10):
        for column in range(1, 10):
            for entry in range(1, 10):
                depends = ["sudoku"]
                for d in range(1, 10):
                    if d == entry:
                        continue
                    # Each entry being set (version 1) requires that the other
                    # entries are not set (version 0)
                    depends.append("%sx%s-is-%s 0" % (row, column, d))

                for other_row in range(1, 10):
                    if other_row == row:
                        continue
                    # If an entry is set, other cells in the same column can't
                    # have the same entry.
                    depends.append("%sx%s-is-%s 0" % (other_row, column, entry))

                for other_column in range(1, 10):
                    if other_column == column:
                        continue
                    # If an entry is set, other cells in the same row can't
                    # have the same entry.
                    depends.append("%sx%s-is-%s 0" % (row, other_column, entry))

                # x - (x - 1)%3 is the largest of 1, 4, 7 that is less than x
                top_corner = (row - (row - 1)%3, column - (column - 1)%3)
                for i in range(9):
                    cell = (top_corner[0] + i//3, top_corner[1] + i%3)
                    # If an entry is set, other cells in the same 3x3 square
                    # can't have the same entry.
                    depends.append("%sx%s-is-%s 0" % (cell[0], cell[1], entry))

                p1 = generate_info("%sx%s-is-%s" % (row, column, entry), 1, depends)
                p0 = generate_info("%sx%s-is-%s" % (row, column, entry), 0, [])
                packages.update({**p0, **p1})

    return packages

# In addition to the usual rules of sudoku, we need to assert that each cell
# has an entry set. We do this by creating nine versions of a metapackage for
# each cell which each depend on an entry.
def generate_cell_metapackages():
    packages = {}
    for row in range(1, 10):
        for column in range(1, 10):
            for entry in range(1, 10):
                p = generate_info("cell-%sx%s" % (row, column), entry,
                    ["%sx%s-is-%s" % (row, column, entry)])
                packages.update(p)

    return packages


# Finally, we have one metapackage "sudoku" that depends on all the "cell"
# metapackages.

def generate_sudoku_metapackage():
    return generate_info("sudoku", 0,
        ["cell-%sx%s" % (row, column)
            for row in range(1, 10)
            for column in range(1, 10)])

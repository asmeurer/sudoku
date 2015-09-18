import sys
from platform import machine
import os
import datetime
import json
import bz2

# Taken from conda.config
_sys_map = {'linux2': 'linux', 'linux': 'linux',
            'darwin': 'osx', 'win32': 'win'}
non_x86_linux_machines = {'armv6l', 'armv7l', 'ppc64le'}
platform = _sys_map.get(sys.platform, 'unknown')
bits = 8 * tuple.__itemsize__

if platform == 'linux' and machine() in non_x86_linux_machines:
    arch_name = machine()
    subdir = 'linux-%s' % arch_name
else:
    arch_name = {64: 'x86_64', 32: 'x86'}[bits]
    subdir = '%s-%d' % (platform, bits)


REPODATA = {
  "info": {
    "arch": arch_name,
    "platform": platform,
  },
  "packages": {}
}

def generate_info(name, build_string, depends):
    return {
        "{name}-a-{build_string}.tar.bz2".format(name=name, build_string=build_string): {
            "build": build_string,
            "build_number": 0,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "depends": depends,
            "name": name,
            "size": 0,
            "version": 'a'
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
                    depends.append("%sx%s-is-%s a f" % (row, column, d))

                for other_row in range(1, 10):
                    if other_row == row:
                        continue
                    # If an entry is set, other cells in the same column can't
                    # have the same entry.
                    depends.append("%sx%s-is-%s a f" % (other_row, column, entry))

                for other_column in range(1, 10):
                    if other_column == column:
                        continue
                    # If an entry is set, other cells in the same row can't
                    # have the same entry.
                    depends.append("%sx%s-is-%s a f" % (row, other_column, entry))

                # x - (x - 1)%3 is the largest of 1, 4, 7 that is less than x
                top_corner = (row - (row - 1)%3, column - (column - 1)%3)
                for i in range(9):
                    cell = (top_corner[0] + i//3, top_corner[1] + i%3)
                    if cell == (row, column):
                        continue
                    # If an entry is set, other cells in the same 3x3 square
                    # can't have the same entry.
                    depends.append("%sx%s-is-%s a f" % (cell[0], cell[1], entry))

                p1 = generate_info("%sx%s-is-%s" % (row, column, entry), 't', depends)
                p0 = generate_info("%sx%s-is-%s" % (row, column, entry), 'f', [])
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
                p = generate_info("cell-%sx%s" % (row, column), str(entry),
                    ["%sx%s-is-%s" % (row, column, entry)])
                packages.update(p)

    return packages


# Finally, we have one metapackage "sudoku" that depends on all the "cell"
# metapackages.

def generate_sudoku_metapackage():
    return generate_info("sudoku", '0',
        ["cell-%sx%s" % (row, column)
            for row in range(1, 10)
            for column in range(1, 10)])

if __name__ == '__main__':
    packages = {
        **generate_sudoku_metapackage(),
        **generate_cell_metapackages(),
        **generate_cells()
        }
    if not os.path.isdir(subdir):
        os.makedirs(subdir)
    with open(os.path.join(subdir, "repodata.json"), 'w') as f:
        r = REPODATA.copy()
        r["packages"] = packages
        data = json.dumps(r, indent=2, sort_keys=True)
        f.write(data)

    with open(os.path.join(subdir, 'repodata.json.bz2'), 'wb') as fo:
        fo.write(bz2.compress(data.encode('utf-8')))

    print("Wrote repodata.json")
    print("Use -c file://" + os.path.abspath("."))

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

def generate_info(name, version, depends):
    return {
        "{name}-{version}-sudoku.tar.bz2".format(name=name, version=version): {
            "build": "sudoku",
            "build_number": 0,
            "date": datetime.date.today().strftime("%Y-%m-%d"),
            "depends": depends,
            "name": name,
            "size": 0,
            "version": str(version)
            }
    }

def all_but(version):
    l = list(range(1, 10))
    l.remove(version)
    return "|".join(map(str, l))

def generate_cells():
    packages = {}
    for row in range(1, 10):
        for column in range(1, 10):
            for entry in range(1, 10):
                depends = ["sudoku"]
                for d in range(1, 10):
                    if d == entry:
                        continue
                    # Each entry being set (t) requires that the other entries
                    # are not set (f)
                    depends.append("%sx%s-is %s" % (row, column, all_but(d)))

                for other_row in range(1, 10):
                    if other_row == row:
                        continue
                    # If an entry is set, other cells in the same column can't
                    # have the same entry.
                    depends.append("%sx%s-is %s" % (other_row, column, all_but(entry)))

                for other_column in range(1, 10):
                    if other_column == column:
                        continue
                    # If an entry is set, other cells in the same row can't
                    # have the same entry.
                    depends.append("%sx%s-is %s" % (row, other_column, all_but(entry)))

                # x - (x - 1)%3 is the largest of 1, 4, 7 that is less than x
                top_corner = (row - (row - 1)%3, column - (column - 1)%3)
                for i in range(9):
                    cell = (top_corner[0] + i//3, top_corner[1] + i%3)
                    if cell == (row, column):
                        continue
                    # If an entry is set, other cells in the same 3x3 square
                    # can't have the same entry.
                    depends.append("%sx%s-is %s" % (cell[0], cell[1], all_but(entry)))

                p = generate_info("%sx%s-is" % (row, column), entry, depends)
                packages.update(p)

    return packages


# Finally, we have one metapackage "sudoku" that depends on all the cell
# metapackages. This ensures that every cell has a number.
def generate_sudoku_metapackage():
    return generate_info("sudoku", '0',
        ["%sx%s-is" % (row, column)
            for row in range(1, 10)
            for column in range(1, 10)])

if __name__ == '__main__':
    packages = {
        **generate_sudoku_metapackage(),
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

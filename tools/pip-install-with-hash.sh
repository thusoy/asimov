#!/bin/sh

# Install and get hash in one step
#
# Downloads the packages to a temporary directory, gets the hash of the
# package and all dependencies, extracts the package names and prints
# a requirements.txt compatible string with the hash

set -e

if [ $# -ne 1 ]; then
    echo >&2 "Usage: $0 <package>"
    exit 1
fi

install_and_get_hash () {
    local dep="$1"
    local dest=$(mktemp -d)

    # install only source releases to avoid having to audit all
    # supported platforms
    pip download "$dep" --no-binary :all: -d "$dest" --quiet
    find "$dest" -type f | while read file; do
        digest=$(sha256sum "$file" | cut -d" " -f1)
        cat <<EOF | python - "$file" "$digest"
import re
import sys
import os.path

filename = sys.argv[1]
digest = sys.argv[2]
package_name = os.path.basename(filename.rsplit('-', 1)[0])
match = re.search('-([0-9\.]+)\.(tar\.gz|zip|tar\.bz2)', filename)
if match is None:
    print 'Could not find version in filename: %s' % filename
    sys.exit()
version = match.groups()[0]
print '%s==%s --hash=sha256:%s' % (package_name, version, digest)
EOF
        pip install "$file" --quiet
    done

    # cleanup
    rm -rf "$dest"
}

install_and_get_hash "$1"

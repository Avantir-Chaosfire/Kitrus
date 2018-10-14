#!/bin/sh

export KitrusInstallDirectory=
export KitrusProjectDirectory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd "$KitrusInstallDirectory"

./root_export.sh
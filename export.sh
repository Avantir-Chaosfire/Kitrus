#!/bin/sh

export KitrusInstallDirectory=
export KitrusProjectDirectory="`dirname \"$0\"`"
cd "$KitrusInstallDirectory"
pwd
./root_export.sh
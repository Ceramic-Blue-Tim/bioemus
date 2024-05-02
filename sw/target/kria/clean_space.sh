#!/bin/bash
# Remove packages no longer required
sudo apt-get autoremove
# Delete all apt cache 
sudo apt-get clean
# Delete journal logs older than 3 days
sudo journalctl --vacuum-time=3d
# Delete older versions of snap packages
set -eu
snap list --all | awk '/disabled/{print $1, $3}' |
	while read snapname revision; do
		snap remove "$snapname" --revision="$revision"
	done
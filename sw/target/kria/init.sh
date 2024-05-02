#!/bin/bash
echo "[BioemuS] Setup environment variables and scripts permissions"
DIR="$( cd "$( dirname -- "$0" )" && pwd )"
export BIOEMUS_PATH="$DIR";
chmod +x $BIOEMUS_PATH/*.sh
chmod +x $BIOEMUS_PATH/app/*.sh
chmod +x $BIOEMUS_PATH/firmware/*.sh
#!/bin/sh

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path_swconfig_json> <debug_mode> <print_swconfig> <sweep_progress>"
    echo "       path_swconfig_json: [*/swconfig*.json]"
    echo "       debug_mode: [true|false]"
    echo "       print_swconfig: [true|false]"
    echo "       sweep_progress: [0..100]"
    exit 1
fi

# Check number of arguments
arg_path_swconfig_json=$1
arg_debug_mode=$2
arg_print_swconfig=$3
arg_sweep_progress=$4

# Activate platform (load device tree and flash bitstream)
$BIOEMUS_PATH/firmware/deactivate.sh
$BIOEMUS_PATH/firmware/activate.sh

# Debug mode
target_exec=""
case $arg_debug_mode in
    true)
        target_exec=debug_bioemus.out
        ;;
    false)
        target_exec=bioemus.out
        ;;
    *)
        echo "Invalid input: $arg_debug_mode. [true|false]"
        exit 1
        ;;
esac

# Print software config loaded
case $arg_print_swconfig in
    true)
        sudo $BIOEMUS_PATH/app/build/$target_exec --fpath-swconfig $1 --print-swconfig --sweep-progress $arg_sweep_progress
        ;;
    false)
        sudo $BIOEMUS_PATH/app/build/$target_exec --fpath-swconfig $1 --sweep-progress $arg_sweep_progress
        ;;
    *)
        echo "Invalid input: $arg_print_swconfig. [true|false]"
        exit 1
        ;;
esac
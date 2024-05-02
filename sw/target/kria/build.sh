#!/bin/bash

TAG="[BioemuS]"
# Define environment variable for BIOEMUS_PATH if not already set
if [ -z "$BIOEMUS_PATH" ]; then
    echo "$TAG Error: BIOEMUS_PATH is not set"
    exit 1
fi

# Define directories
DRIVERS_DIR="$BIOEMUS_PATH/drivers"
FIRMWARE_DIR="$BIOEMUS_PATH/firmware"
SOFTWARE_DIR="$BIOEMUS_PATH/app"

# Function to build drivers
build_drivers() {
    echo "$TAG Building drivers..."
    cd $DRIVERS_DIR/dma_proxy || exit 1
    make clean
    make
}

# Function to build firmware
build_firmware() {
    echo "$TAG Building firmware..."
    $FIRMWARE_DIR/build.sh
}

# Function to build software
build_software() {
    echo "$TAG Building software..."
    cd "$SOFTWARE_DIR" || exit 1
    make
}

# Function to clean builds
clean() {
    echo "$TAG Cleaning builds..."
    echo "$TAG Clean application build"
    cd $SOFTWARE_DIR || exit 1
    make clean

    echo "$TAG Clean drivers build"
    cd $DRIVERS_DIR/dma_proxy/ || exit 1
    make clean

    echo "$TAG Clean firmware build"
    cd $FIRMWARE_DIR || exit 1
    make clean

    echo "$TAG Clean installed firmware"
    sudo rm -r /lib/firmware/xilinx/kr260-bioemus

    echo "$TAG Clean environment variables"
    unset $BIOEMUS_PATH;

    cd
}

# Main function to handle options
main() {
    case $1 in
        drivers)
            build_drivers
            ;;
        firmware)
            build_firmware
            ;;
        software)
            build_software
            ;;
        clean)
            clean
            ;;
        all|"")
            build_drivers
            build_firmware
            build_software
            ;;
        *)
            echo "$TAG Invalid option: $1"
            echo "$TAG Usage: $0 [drivers|firmware|software|all|clean]"
            exit 1
            ;;
    esac
}

main "$@"
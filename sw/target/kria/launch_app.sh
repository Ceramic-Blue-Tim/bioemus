# Check arguments and usage guide
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path_swconfig_json> <debug_mode> <print_swconfig> <sweep_progress>"
    echo "       path_swconfig_json: [*/swconfig*.json]"
    echo "       debug_mode: [true|false]"
    echo "       print_swconfig: [true|false]"
    echo "       sweep_progress: [0..100]"
    exit 1
fi

# Application parameters
path_swconfig_json=$1
debug_mode="true"
print_swconfig="false"
sweep_progress=100

# Launch application
$BIOEMUS_PATH/app/run.sh $path_swconfig_json $debug_mode $print_swconfig $sweep_progress
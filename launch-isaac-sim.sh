#!/bin/bash
set -e

PYTHON_SCRIPT_PATH="./replace_config_path.py"
CONFIG_PATH=""

usage() {
    echo "Usage: $0 -config /path/to/your/config/file [options]"
    echo
    echo "Script to launch IsaacSim with custom path of config file"
    echo "Must be executed from the isaacsim directory."
    echo
    echo "Options:"
    echo "  -h, --help            Show this help message and exit"
    echo "  -config <path>        REQUIRED: Absolute path to the isaacsim.replicator.agent config file to use"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -config)
            if [ -n "$2" ] && [[ "$2" != -* ]]; then
                CONFIG_PATH="$2"
                shift 2
            else
                echo "Error: -config requires a path argument."
                usage
            fi
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

if [ -z "$CONFIG_PATH" ]; then
    echo "Error: The -config argument is mandatory. Please provide the path to your config file."
    usage
fi

if [ ! -f "$PYTHON_SCRIPT_PATH" ]; then
    echo "Error: Python script not found at '$PYTHON_SCRIPT_PATH'."
    exit 1
fi

echo "--- Setting Custom Config Path ---"
echo "Running Python script to inject path: $CONFIG_PATH"

python3 "$PYTHON_SCRIPT_PATH" "$CONFIG_PATH"
PYTHON_EXIT_CODE=$?

if [ "$PYTHON_EXIT_CODE" -ne 0 ]; then
    echo "Error: Python script failed (Exit Code: $PYTHON_EXIT_CODE). Aborting launch."
    exit 1
fi

echo "Path injection successful."
echo "-------------------------------------"

echo "launching the isaac-sim selector application"
./isaac-sim.selector.sh
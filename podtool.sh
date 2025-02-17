#!/usr/bin/env bash
# podtool.sh - A simple CLI tool distributed as a Nix package

# Exit immediately if a command exits with a non-zero status,
# if an undefined variable is used, or if any command in a pipe fails.
set -euo pipefail

# Define a version for the tool
VERSION="1.0.0"

# Show usage/help information.
show_help() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] COMMAND

Options:
  -h, --help         Display this help message.

Commands:
  greet              Print a greeting message.
  version            Show version information.
  mix [-o output] file1 file2 ...
                     Mix provided audio files into a joined audio file.
                     If -o is not specified, the output file defaults to "mixed.wav".
  recode [-o output] file
                     Convert provided audio file to MP3 format with high quality settings.
                     If -o is not specified, the output file defaults to "recode.mp3".

Examples:
  $(basename "$0") mix song1.wav song2.wav
  $(basename "$0") mix -o output.wav track1.wav track2.wav
  $(basename "$0") recode input.wav
  $(basename "$0") recode -o output.mp3 input.wav
EOF
}

# If no arguments are provided, then show help.
if [ "$#" -eq 0 ]; then
    show_help
    exit 1
fi

# Parse the command/option provided.
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    greet)
        echo "Hello from podtool version $VERSION!"
        ;;
    version)
        echo "podtool version $VERSION"
        ;;
    mix)
        shift
        if [ "$#" -lt 1 ]; then
            echo "Error: 'mix' command requires at least one input audio file."
            exit 1
        fi

        OUTPUT="mix.wav"
        if [ "$1" = "-o" ]; then
            shift
            if [ "$#" -lt 2 ]; then
                echo "Error: When using -o, please provide an output file name and at least one input file."
                exit 1
            fi
            OUTPUT="$1"
            shift
        fi

        echo "Mixing audio files into ${OUTPUT}..."
        CMD_SOX -m "$@" "${OUTPUT}"
        echo "Audio files mixed successfully into ${OUTPUT}."
        ;;
    recode)
        shift
        if [ "$#" -lt 1 ]; then
            echo "Error: 'recode' command requires an input audio file."
            exit 1
        fi

        OUTPUT="mix.mp3"
        if [ "$1" = "-o" ]; then
            shift
            if [ "$#" -lt 2 ]; then
                echo "Error: When using -o, please provide an output file name and an input file."
                exit 1
            fi
            OUTPUT="$1"
            shift
        fi

        if [ "$#" -ne 1 ]; then
            echo "Error: 'recode' command expects exactly one input file."
            exit 1
        fi

        INPUT="$1"
        echo "Converting ${INPUT} to MP3 format with high quality settings into ${OUTPUT}..."
        CMD_FFMPEG -y -i "${INPUT}" -codec:a libmp3lame -qscale:a 0 "${OUTPUT}"
        echo "Conversion complete. Output file: ${OUTPUT}"
        ;;
    *)
        echo "Error: Unknown command: $1"
        show_help
        exit 1
        ;;
esac 
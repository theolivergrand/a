#!/bin/bash

# Convenience script to run ctags from project root
# This script forwards all arguments to the main ctags script

exec "$(dirname "$0")/ctags_files/update_ctags.sh" "$@"

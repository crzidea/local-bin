#!/bin/bash
current_dir=$(basename "$PWD")
prefix=${current_dir%-specs}
exec gemini --include-directories "../${prefix}-server,../${prefix}-web" "$@"

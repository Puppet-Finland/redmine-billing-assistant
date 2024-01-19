#!/bin/bash
OUT_DIR="${REDREP_REPORTS_DIR-./reports}"
echo "Using output dir: $OUT_DIR."

podman run -v "$OUT_DIR":/app/reports:Z redrep "$@"

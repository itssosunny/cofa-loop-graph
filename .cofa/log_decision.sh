#!/usr/bin/env bash
# log_decision.sh — Append a sanitized, structured row to the decision log (TSV).
# Usage: bash .cofa/log_decision.sh "<phase>" "<decision>" "<why_and_rejected_alt>" "<evidence>" "<result>" [logfile]
# Default logfile: .cofa/decisions.tsv
set -euo pipefail

if [ "$#" -lt 5 ]; then
    printf 'Usage: %s "<phase>" "<decision>" "<why_and_rejected_alt>" "<evidence>" "<result>" [logfile]\n' "$0" >&2
    printf 'Example: bash .cofa/log_decision.sh "T+15m" "Use in-memory dict" "Read-heavy; rejected Redis" "latency < 2ms" "PASS"\n' >&2
    exit 1
fi

phase="$1"
decision="$2"
why_and_rejected_alt="$3"
evidence="$4"
result="$5"
logfile="${6:-.cofa/decisions.tsv}"

logdir="$(dirname "$logfile")"
if [ -n "$logdir" ] && [ "$logdir" != "." ] && [ ! -d "$logdir" ]; then
    mkdir -p "$logdir"
fi

# Auto-create header if logfile is absent or empty
if [ ! -s "$logfile" ]; then
    printf 'ts\tphase\tdecision\twhy_and_rejected_alt\tevidence\tresult\n' >> "$logfile"
fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Sanitize tabs, newlines, and formula injection characters (=, +, -, @)
clean() {
    local v
    v=$(printf '%s' "$1" | tr '\t\n\r' '   ')
    case "$v" in
        =*|+*|-*|@*) printf "'%s" "$v" ;;
        *) printf '%s' "$v" ;;
    esac
}

printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$ts" \
    "$(clean "$phase")" \
    "$(clean "$decision")" \
    "$(clean "$why_and_rejected_alt")" \
    "$(clean "$evidence")" \
    "$(clean "$result")" \
    >> "$logfile"

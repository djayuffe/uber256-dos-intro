#!/bin/sh
# Assemble UBER256.COM with NASM and enforce the 256-byte limit.
set -eu
cd "$(dirname "$0")"
command -v nasm >/dev/null 2>&1 || { echo 'ERROR: NASM is required.' >&2; exit 1; }
nasm -f bin -Wall -Werror intro256.asm -o UBER256.COM
size=$(wc -c < UBER256.COM | tr -d ' ')
printf 'UBER256.COM: %s bytes (limit 256, %s to spare)\n' "$size" "$((256 - size))"
[ "$size" -le 256 ] || { echo 'ERROR: UBER256.COM exceeds 256 bytes' >&2; exit 2; }
if command -v sha256sum >/dev/null 2>&1; then sha256sum UBER256.COM > SHA256SUMS; else shasum -a 256 UBER256.COM > SHA256SUMS; fi
cat SHA256SUMS

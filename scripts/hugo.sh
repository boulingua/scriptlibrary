#!/usr/bin/env sh
set -eu
LIBRARY_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ -d "$LIBRARY_ROOT/.tools/go/bin" ]; then
  PATH="$LIBRARY_ROOT/.tools/go/bin:$LIBRARY_ROOT/.tools/hugo:$PATH"
  export PATH
fi
cd "$LIBRARY_ROOT"
exec hugo "$@"

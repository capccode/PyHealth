#!/usr/bin/env bash
# Acceptance checks for the PyHealth 2.0 hardening pass.
# See ACCEPTANCE_CRITERIA.md for the rationale behind each criterion.
#
# Usage: tools/check_acceptance.sh [--fast]
#   --fast  skip the two full unittest suite runs (C1/C2), which take ~10 min.
#
# Set PYTHON to the interpreter of the environment with pyhealth installed
# (defaults to "python").

set -u
PYTHON="${PYTHON:-python}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

FAST=0
[ "${1:-}" = "--fast" ] && FAST=1

pass=0
fail=0

report() { # name, status (0 ok)
    if [ "$2" -eq 0 ]; then
        echo "PASS: $1"
        pass=$((pass + 1))
    else
        echo "FAIL: $1"
        fail=$((fail + 1))
    fi
}

if [ "$FAST" -eq 0 ]; then
    # C1: tests/core exits 0 (failures/errors break the build; skips allowed)
    "$PYTHON" -m unittest discover -t . -s tests/core -p 'test_*.py' \
        -v > /tmp/acceptance-core.txt 2>&1
    report "C1 tests/core suite (0 failures, 0 errors)" $?

    # C2: every skip reason is on the documented allowlist
    "$PYTHON" - <<'EOF'
import re, sys
allow = re.compile(
    r"CUDA not available"
    r"|torch-geometric (not installed|required)"
    r"|torchaudio not available"
    r"|Hugging Face Hub not accessible"
    r"|StageNet with discrete codes requires special handling"
    r"|noteevents not included in test resources"
    r"|Shape mismatch handling depends on implementation details"
)
bad = []
for line in open("/tmp/acceptance-core.txt"):
    m = re.search(r"skipped ['\"](.+?)['\"]", line)
    if m and not allow.search(m.group(1)):
        bad.append(m.group(1))
if bad:
    print("Undocumented skip reasons:", sorted(set(bad)))
sys.exit(1 if bad else 0)
EOF
    report "C2 skip reasons all on allowlist" $?

    # C3: tests/nlp exits 0
    "$PYTHON" -m unittest discover -t . -s tests/nlp -p 'test_*.py' \
        > /tmp/acceptance-nlp.txt 2>&1
    report "C3 tests/nlp suite" $?
else
    echo "SKIP: C1-C3 (--fast)"
fi

# C4: architecture contracts (clean imports + task schema contract)
"$PYTHON" tools/check_task_contracts.py > /tmp/acceptance-contracts.txt 2>&1
report "C4 architecture contracts (imports + task schemas)" $?

# C5: documented quickstart pipeline runs end-to-end on bundled fixture
"$PYTHON" tools/check_quickstart.py > /tmp/acceptance-quickstart.txt 2>&1
report "C5 quickstart pipeline on test-resources fixture" $?

# C6: documented quickstart imports resolve
"$PYTHON" - <<'EOF' >/dev/null 2>&1
from pyhealth.datasets import MIMIC3Dataset, MIMIC4Dataset, split_by_patient, get_dataloader
from pyhealth.tasks import MortalityPredictionMIMIC3, ReadmissionPredictionMIMIC3
from pyhealth.models import RNN, Transformer, MLP
from pyhealth.trainer import Trainer
EOF
report "C6 documented quickstart imports" $?

# C7: no stale third-party references in docs (combo library, old forks).
# ycq091044.github.io in about.rst is a legitimate author homepage.
if grep -rEn "yzhao062|github\.com/ycq091044|\bcombo\b" docs/ --include="*.rst" >/dev/null 2>&1; then
    report "C7 no stale repo references in docs" 1
else
    report "C7 no stale repo references in docs" 0
fi

# C8: no unlabeled PyHealth 1.x video links (must say "1.x legacy")
if grep -rEn "PyHealth 1\.(6|16)\)" docs/ --include="*.rst" >/dev/null 2>&1; then
    report "C8 1.x tutorial videos labeled as legacy" 1
else
    report "C8 1.x tutorial videos labeled as legacy" 0
fi

# C9: no environment-specific example paths in package source
if grep -rn "/srv/local" pyhealth/ --include="*.py" >/dev/null 2>&1; then
    report "C9 no /srv/local paths in pyhealth/" 1
else
    report "C9 no /srv/local paths in pyhealth/" 0
fi

# C10: changelog has a PyHealth 2.0 entry
grep -q "PyHealth 2.0 release" docs/log.rst
report "C10 changelog covers the 2.0 release" $?

echo
echo "passed=$pass failed=$fail"
[ "$fail" -eq 0 ]

#!/bin/sh
# The autorouter is not deterministic. Build the same placement many times in parallel and score each
# (lens.py): clock-pair skew, data spread, USB pair match. Keep the best fully-connected result.
cd "$(dirname "$0")"; rm -rf work_* log_*.txt
i=0
for v in "270 -5.0" "90 -5.0"; do
  for s in 1 2 3 4 5 6 7 8 9 10; do
    set -- $v; i=$((i+1)); ( HR_ROT=$1 HR_DY=$2 WORK=work_$i ./build.sh > log_$i.txt 2>&1; echo "cfg $1 $2" >> log_$i.txt ) &
  done
done
wait
for f in log_*.txt; do
  if grep -q "unconnected 0 " $f && ! grep -q "courtyards_overlap\|'clearance'\|shorting" $f; then echo "$(grep SCORE $f) | $(grep cfg $f) | $f"; fi
done | sort -t' ' -k2 -n

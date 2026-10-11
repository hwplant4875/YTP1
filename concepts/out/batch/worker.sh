#!/bin/bash
# render worker: claims queued shorts one at a time (mkdir lock), exits when STOP exists and the queue is drained
B=/home/user/YTP1/concepts/out/batch
while true; do
  got=
  for n in $(cat $B/queue.txt 2>/dev/null); do
    if mkdir $B/$n/claim 2>/dev/null; then got=$n; break; fi
  done
  if [ -n "$got" ]; then echo "$(date -u +%T) start $got" >> $B/worker.log; $B/job.sh $got; echo "$(date -u +%T) end $got $(ls $B/$got | tr '\n' ' ')" >> $B/worker.log
  else [ -f $B/STOP ] && exit 0; sleep 20; fi
done

cd /tmp/claude-0/sp
node render.mjs main.mjs 30 0 123 out/p1.mp4 &
node render.mjs main.mjs 30 123 246 out/p2.mp4 &
node render.mjs main.mjs 30 246 369 out/p3.mp4 &
node render.mjs main.mjs 30 369 491.334 out/p4.mp4 &
wait
printf "file 'p1.mp4'\nfile 'p2.mp4'\nfile 'p3.mp4'\nfile 'p4.mp4'\n" > out/list.txt
ffmpeg -y -v error -f concat -safe 0 -i out/list.txt -c copy out/video.mp4 && echo RENDER_DONE

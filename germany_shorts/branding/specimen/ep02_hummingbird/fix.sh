cd /tmp/claude-0/hb2
node render.mjs main.mjs 60 64.2666667 93.2 out/p1b.mp4 &
node render.mjs main.mjs 60 186.4 233 out/p3a.mp4 &
node render.mjs main.mjs 60 233 279.6 out/p3b.mp4 &
wait
printf "file 'p1.mp4'\nfile 'p1b.mp4'\nfile 'p2.mp4'\nfile 'p3a.mp4'\nfile 'p3b.mp4'\nfile 'p4.mp4'\n" > out/list.txt
ffmpeg -y -v error -f concat -safe 0 -i out/list.txt -c copy out/video.mp4 && echo RENDER_DONE

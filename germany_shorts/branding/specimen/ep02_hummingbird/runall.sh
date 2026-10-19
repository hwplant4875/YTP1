cd /tmp/claude-0/hb2
node render.mjs main.mjs 60 0 93.2 out/p1.mp4 &
node render.mjs main.mjs 60 93.2 186.4 out/p2.mp4 &
node render.mjs main.mjs 60 186.4 279.6 out/p3.mp4 &
node render.mjs main.mjs 60 279.6 372.71 out/p4.mp4 &
wait
printf "file 'p1.mp4'\nfile 'p2.mp4'\nfile 'p3.mp4'\nfile 'p4.mp4'\n" > out/list.txt
ffmpeg -y -v error -f concat -safe 0 -i out/list.txt -c copy out/video.mp4 && echo RENDER_DONE

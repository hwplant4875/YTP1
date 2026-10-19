cd /tmp/claude-0/sp2
node render.mjs main2.mjs 60 0 108.5 out/p1.mp4 &
node render.mjs main2.mjs 60 108.5 217 out/p2.mp4 &
node render.mjs main2.mjs 60 217 325.5 out/p3.mp4 &
node render.mjs main2.mjs 60 325.5 433.35 out/p4.mp4 &
wait
printf "file 'p1.mp4'\nfile 'p2.mp4'\nfile 'p3.mp4'\nfile 'p4.mp4'\n" > out/list.txt
ffmpeg -y -v error -f concat -safe 0 -i out/list.txt -c copy out/video.mp4 && echo RENDER_DONE

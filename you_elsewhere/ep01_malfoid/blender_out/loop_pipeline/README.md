# Long-video pipeline (loop + overlay)

1. `malfoid_blender.py ... loop` (via `render_loop.sh`): renders 22 s of the background only (no watermark, spectrum or fade), about 2.8 s/frame.
2. `make_loop.py frames_loop loop20_v1.mp4`: crossfades the last 2 s into the start, giving a seamless 20 s loop (CRF 12 master, kept on the laptop:
   `C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep01_malfoid\loop20_v1.mp4`, 104 MB).
3. `composite.py loop20_v1.mp4 <music> <fire_bed> <seconds> <out.mp4> <assets>`: loops the plate and adds the 60 % -> 100 % smoothstep fade over the first 5 s,
   the Allura watermark, and the small sharp spectrum (64 mirrored spikes, 40 Hz - 1.5 kHz, 35 %). The audio is the music plus the fire bed
   looped with equal-power crossfades, 15 LU under the music. About 0.052 s/frame, so a 1-hour video takes roughly 95 min (CPU x264).

`malfoid_composite_test60.mp4`: 60 s test with the suite audio and the fire bed. The loop seam at 20 s and 40 s is within normal frame-to-frame variation.

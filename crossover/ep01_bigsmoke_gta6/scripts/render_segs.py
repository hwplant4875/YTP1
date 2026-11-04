"""Segment-cached render: python3 -I scripts/render_segs.py edl.py out.mp4
Each shot -> segs/<edlname>/<id>_<hash>.mp4 (crf 12); re-renders only changed shots; concat -> out (crf 16)."""
import sys, os, json, hashlib, subprocess, importlib.util, time
sys.argv_saved=list(sys.argv)
exec(open('scripts/render.py').read().split('def main')[0])
path,out=sys.argv_saved[1],sys.argv_saved[2]
spec=importlib.util.spec_from_file_location('edl',path); edl=importlib.util.module_from_spec(spec); spec.loader.exec_module(edl)
sd=f"segs/{os.path.splitext(os.path.basename(path))[0]}"; os.makedirs(sd,exist_ok=True)
lst=[]; marks=[]; total=0; t0=time.time()
for s in edl.SHOTS:
    h=hashlib.md5(json.dumps(s,sort_keys=True,default=str).encode()+open('scripts/render.py','rb').read()).hexdigest()[:10]
    f=f"{sd}/{s['id']}_{h}.mp4"
    n=int(round(s['dur']*FPS))
    if not os.path.exists(f):
        enc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p',f+'.tmp.mp4'],stdin=subprocess.PIPE)
        gen=render_comp(s) if s['type']=='comp' else render_plate(s)
        c=0
        for fr in gen: enc.stdin.write(fr.tobytes()); c+=1
        enc.stdin.close(); enc.wait(); os.rename(f+'.tmp.mp4',f)
        print('rendered',s['id'],c,'frames',round(time.time()-t0,1),'s',flush=True)
    lst.append(f); marks.append((s['id'],round(total/FPS,3),n)); total+=n
open(sd+'/list.txt','w').write(''.join(f"file '{os.path.abspath(x)}'\n" for x in lst))
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',sd+'/list.txt','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p','-r','30','-movflags','+faststart',out],check=True)
json.dump(marks,open(out+'.marks.json','w'))
print('done',total,'frames',round(total/FPS,2),'s')

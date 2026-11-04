import json, subprocess, sys, os
O=json.load(open('hd/offsets.json'))
def grab(key, t_off, out, w=480):
    f='hd/'+O[key]['file']; t=t_off-O[key]['offset']
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',f'{t:.3f}','-i',f,'-frames:v','1','-vf',f"scale={w}:-2,drawtext=text='{key} {t_off}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6",out],check=True)
if __name__=='__main__':
    outdir=sys.argv[1]; os.makedirs(outdir,exist_ok=True)
    for i,spec in enumerate(sys.argv[2:]):
        k,t=spec.split('@'); grab(k,float(t),f'{outdir}/{i:03d}.jpg')

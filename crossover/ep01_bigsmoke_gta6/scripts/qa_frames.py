"""qa_frames.py video.mp4 marks.json outdir : frames at each shot start+2f, middle, end-2f -> contact sheets"""
import sys,json,subprocess,os,cv2,numpy as np
v,mk,od=sys.argv[1:4]; os.makedirs(od,exist_ok=True)
marks=json.load(open(mk)); ims=[]
for sid,t0,n in marks:
    for k,fi in [('a',2),('m',n//2),('z',n-3)]:
        t=t0+fi/30; f=f'{od}/{sid}_{k}.jpg'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',f'{t:.3f}','-i',v,'-frames:v','1','-vf','scale=480:-2',f])
        im=cv2.imread(f); cv2.putText(im,f'{sid}{k} {t:.2f}',(6,22),0,0.6,(0,255,255),2); ims.append(im)
rows=[np.hstack(ims[i:i+6]) for i in range(0,len(ims)-len(ims)%6,6)]
if len(ims)%6: 
    r=ims[len(ims)-len(ims)%6:]; r+= [np.zeros_like(ims[0])]*(6-len(r)); rows.append(np.hstack(r))
for i in range(0,len(rows),6):
    cv2.imwrite(f'{od}/sheet_{i//6}.jpg',np.vstack(rows[i:i+6]),[cv2.IMWRITE_JPEG_QUALITY,80])
print('sheets',(len(rows)+5)//6)

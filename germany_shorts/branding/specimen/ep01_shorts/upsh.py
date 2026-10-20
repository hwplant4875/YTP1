# upload one X-Ray Zoo short: private + publishAt, family audience (not made for kids)
import os,json,urllib.request,urllib.parse,sys
sid=sys.argv[1]; M=json.load(open('/tmp/claude-0/up/shorts.json'))[sid]
d=urllib.parse.urlencode({'client_id':os.environ['YT_CLIENT_ID'],'client_secret':os.environ['YT_CLIENT_SECRET'],'refresh_token':os.environ['YT_REFRESH_TOKEN_FP'],'grant_type':'refresh_token'}).encode()
H={'Authorization':'Bearer '+json.load(urllib.request.urlopen('https://oauth2.googleapis.com/token',d))['access_token']}
tags=M['tags']+['great white shark','shark facts','shark anatomy','biology','learn science','science shorts','animal facts','marine biology','x-ray zoo']
desc=M['desc']+'\n\nFull look inside a great white shark: https://youtu.be/AZe_m1agf4E'+('\n\n'+M['credit'] if M.get('credit') else '')+'\n\n#shorts #shark #science'
body={'snippet':{'title':M['title'],'description':desc,'tags':tags,'categoryId':'27','defaultLanguage':'en','defaultAudioLanguage':'en'},
 'status':{'privacyStatus':'private','publishAt':M['at'],'selfDeclaredMadeForKids':False,'embeddable':True,'license':'youtube'}}
vid=M['file']; size=os.path.getsize(vid)
r=urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',data=json.dumps(body).encode(),headers={**H,'Content-Type':'application/json; charset=UTF-8','X-Upload-Content-Length':str(size),'X-Upload-Content-Type':'video/mp4'},method='POST')
loc=urllib.request.urlopen(r).headers['Location']
v=json.load(urllib.request.urlopen(urllib.request.Request(loc,data=open(vid,'rb').read(),headers={**H,'Content-Type':'video/mp4'},method='PUT'),timeout=900))
print(sid,v['id'],v['status']['privacyStatus'],v['status'].get('publishAt'))

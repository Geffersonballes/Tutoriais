import sys; sys.path.insert(0,'/home/user/Tutoriais/tiktok-geopolitica/motor')
from PIL import Image, ImageDraw, ImageFont
import os
F='/home/user/Tutoriais/tiktok-geopolitica/assets/fonts/Montserrat[wght].ttf'
def fo(t,w=b"Black"):
    f=ImageFont.truetype(F,t)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
AM=(255,204,0); VM=(220,40,40); BR=(255,255,255)
import json
caps=[(f"PEÇA {i+1}",t) for i,t in enumerate(json.load(open("caps.json")))]
N=len(caps)
W,H=1920,1080; vx0=(W-608)//2
def lateral(n, rot, sub, name):
    # transparent overlay with side texts for main segments
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    cx=vx0//2
    d.rounded_rectangle((cx-150,380,cx+150,450),20,fill=VM)
    d.text((cx,415),rot,font=fo(44),fill=BR,anchor='mm')
    y=520
    for line in sub.split('\n'):
        d.text((cx,y),line,font=fo(54),fill=BR,anchor='mm',stroke_width=4,stroke_fill=(0,0,0)); y+=70
    rx=vx0+608+cx
    d.text((rx,420),"COMO FUNCIONAM",font=fo(40,b"ExtraBold"),fill=BR,anchor='mm',stroke_width=3,stroke_fill=(0,0,0))
    d.text((rx,480),"OS GAMES",font=fo(60),fill=AM,anchor='mm',stroke_width=4,stroke_fill=(0,0,0))
    d.text((rx,550),"POR DENTRO",font=fo(60),fill=AM,anchor='mm',stroke_width=4,stroke_fill=(0,0,0))
    # progress dots
    for i in range(N):
        x=rx-(N-1)*20+i*40; c=AM if i<=n else (90,90,90)
        d.ellipse((x-12,640-12,x+12,640+12),fill=c)
    d.text((rx,940),"PEÇA POR PEÇA",font=fo(34,b"ExtraBold"),fill=BR,anchor='mm')
    d.text((W-40,1040),"Conteúdo gerado com IA",font=fo(24,b"SemiBold"),fill=(220,220,220),anchor='rm')
    im.save(name)
def wrap(s):
    w=s.split()
    if len(s)<14: return s
    best=min(range(1,len(w)),key=lambda h:abs(len(" ".join(w[:h]))-len(" ".join(w[h:]))))
    return " ".join(w[:best])+"\n"+" ".join(w[best:])
for i,(r,s) in enumerate(caps): lateral(i,r,wrap(s),f'lat{i}.png')
# full-screen chapter cards + title + end
def card(name, top, big, small=None):
    im=Image.new('RGB',(W,H),(14,16,22)); d=ImageDraw.Draw(im)
    for k in range(0,W,6): d.line((k,0,k-300,H),fill=(18,20,28))
    if top:
        d.rounded_rectangle((W//2-170,330,W//2+170,410),22,fill=VM); d.text((W//2,370),top,font=fo(52),fill=BR,anchor='mm')
    yy=520
    for line in big.split('\n'):
        t=120
        while fo(t).getbbox(line,stroke_width=6)[2]>1800: t-=6
        d.text((W//2,yy),line,font=fo(t),fill=AM if not top else BR,anchor='mm',stroke_width=6,stroke_fill=(0,0,0)); yy+=140
    if small: d.text((W//2,yy+20),small,font=fo(46,b"ExtraBold"),fill=BR,anchor='mm')
    d.text((W-40,1040),"Conteúdo gerado com IA",font=fo(24,b"SemiBold"),fill=(200,200,200),anchor='rm')
    im.save(name)
for i,(r,s) in enumerate(caps): card(f'card{i}.png',r,s.upper())
card('titulo.png',None,"GTA 6 E OS GAMES\nPOR DENTRO","explicados peça por peça")
card('fim.png',None,"SE INSCREVE\nPARA A PRÓXIMA PEÇA","PEÇA POR PEÇA")

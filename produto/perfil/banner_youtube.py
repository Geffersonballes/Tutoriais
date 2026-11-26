"""Banner do YouTube (2560x1440) na identidade do mascote: recorta o mascote e a ilha do render 3D da capa do Facebook."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=os.path.dirname(os.path.abspath(__file__)); FONTS="/home/user/Tutoriais/tiktok-geopolitica/assets/fonts"
def fonte(t,p):
    f=ImageFont.truetype(os.path.join(FONTS,"Montserrat[wght].ttf"),t); f.set_variation_by_axes([p]); return f
src=Image.open(os.path.join(D,"capa_facebook_3d.jpg")).convert("RGB"); a=np.asarray(src).astype(int)
bg=np.array([41,105,255]); dist=np.sqrt(((a-bg)**2).sum(2))
alpha=np.clip((dist-28)*6,0,255).astype(np.uint8)
rgba=src.copy(); rgba.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1)))
masc=rgba.crop((225,25,610,540)); ilha=rgba.crop((965,70,1590,575))
W,H=2560,1440; BG=(41,105,255)
im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
# chão um pouco mais claro como no render
d.rectangle((0,820,W,H),fill=(47,110,255))
def cola(img,h,x,ybase):
    w=int(img.width*h/img.height); r=img.resize((w,h),Image.LANCZOS)
    # sombra
    sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).ellipse((x+w*0.15,ybase-22,x+w*0.95,ybase+22),fill=90)
    im.paste((20,60,180),(0,0),sh.filter(ImageFilter.GaussianBlur(18)))
    im.paste(r,(x,ybase-h),r)
    return w
cola(masc,425,540,935)
cola(ilha,370,1580,925)
CX=1180
def linha(t,y,f,cor,s=7):
    w=d.textlength(t,font=f); x=CX-w/2
    d.text((x+s,y+s),t,font=f,fill=(10,30,90)); d.text((x,y),t,font=f,fill=cor)
linha("Como isso funciona? Eu explico.",520,fonte(44,700),(255,255,255),3)
linha("PEÇA POR",585,fonte(128,900),(255,255,255))
linha("PEÇA",715,fonte(128,900),(255,214,10))
t="GAMES  •  GEOPOLÍTICA  •  EM 3D"; f=fonte(34,800); w=d.textlength(t,font=f)
d.rounded_rectangle((CX-w/2-28,868,CX+w/2+28,924),28,fill=(255,255,255)); d.text((CX-w/2,876),t,font=f,fill=(25,60,160))
im.save(os.path.join(D,"banner_youtube.png"))
p=im.copy(); pd=ImageDraw.Draw(p)
pd.rectangle(((W-1546)//2,(H-423)//2,(W+1546)//2,(H+423)//2),outline=(0,255,0),width=5)
pd.rectangle((0,(H-423)//2,W-1,(H+423)//2),outline=(255,255,0),width=3)
p.resize((1280,720)).save(os.path.join(D,"banner_youtube_previa.jpg"))
Image.open(os.path.join(D,"foto_perfil_tiktok.jpg")).resize((800,800),Image.LANCZOS).save(os.path.join(D,"foto_youtube.png"))

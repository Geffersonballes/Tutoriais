from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='/home/user/Tutoriais/tiktok-geopolitica/assets/fonts/Montserrat[wght].ttf'
def fo(t):
    f=ImageFont.truetype(F,t)
    try: f.set_variation_by_name(b"Black")
    except Exception: pass
    return f
S=800*3; AM=(255,204,0); VM=(220,40,40); BG=(14,16,22)
im=Image.new('RGB',(S,S),BG); d=ImageDraw.Draw(im)
for k in range(-S,S,42): d.line((k,0,k+S,S),fill=(20,23,32),width=9)
def peca(cx,cy,a,cor,dx=0):
    m=Image.new('L',(S,S),0); md=ImageDraw.Draw(m)
    x0,y0=cx-a//2,cy-a//2; r=int(a*0.19)
    md.rounded_rectangle((x0,y0,x0+a,y0+a),int(a*0.08),fill=255)
    md.ellipse((cx-r,y0-int(r*1.55),cx+r,y0+int(r*0.45)),fill=255)        # pino em cima
    md.ellipse((x0+a-int(r*0.45),cy-r,x0+a+int(r*1.55),cy+r),fill=255)    # pino à direita
    md.ellipse((x0-int(r*0.45),cy-r,x0+int(r*1.55),cy+r),fill=0)          # encaixe à esquerda
    sh=m.filter(ImageFilter.GaussianBlur(40))
    im.paste((0,0,0),(30,40),Image.eval(sh,lambda v:int(v*0.6)))
    im.paste(cor,(0,0),m)
peca(int(S*0.47),int(S*0.53),int(S*0.46),AM)
d=ImageDraw.Draw(im)
# peça vermelha menor chegando (encaixe)
m=Image.new('L',(S,S),0)
d.text((int(S*0.52),int(S*0.555)),"PP",font=fo(int(S*0.16)),fill=BG,anchor='mm')
im=im.resize((800,800),Image.LANCZOS); im.save('foto_canal.png')
c=im.copy(); mask=Image.new('L',(800,800),0); ImageDraw.Draw(mask).ellipse((0,0,799,799),fill=255)
out=Image.new('RGB',(800,800),(255,255,255)); out.paste(c,(0,0),mask)
small=out.resize((98,98),Image.LANCZOS)
pv=Image.new('RGB',(1100,820),(255,255,255)); pv.paste(out,(0,10)); pv.paste(small,(900,360)); pv.save('foto_previa.jpg')

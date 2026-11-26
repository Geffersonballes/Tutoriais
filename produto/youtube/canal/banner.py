from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
F='/home/user/Tutoriais/tiktok-geopolitica/assets/fonts/Montserrat[wght].ttf'
def fo(t,w=b"Black"):
    f=ImageFont.truetype(F,t)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
W,H=2560,1440; AM=(255,204,0); VM=(220,40,40); BR=(255,255,255)
im=Image.new('RGB',(W,H),(14,16,22)); d=ImageDraw.Draw(im)
for k in range(-H,W,14): d.line((k,0,k+H,H),fill=(19,22,30),width=3)
# faixa de cenas próprias (fora e dentro da área segura, escurecidas)
tiles=[Image.open(f'st{i}.jpg').convert('RGB') for i in range(8)]
x=-50
for i in [0,1,2,3]:
    t=tiles[i]
    t=ImageEnhance.Brightness(t).enhance(0.42)
    im.paste(t,(x,H//2-170)); x+=680
# vinheta sobre a faixa
ov=Image.new('L',(W,H),0); od=ImageDraw.Draw(ov)
od.rectangle((507,H//2-230,W-507,H//2+230),fill=170)
ov=ov.filter(ImageFilter.GaussianBlur(60))
im=Image.composite(Image.new('RGB',(W,H),(10,12,18)),im,ov); d=ImageDraw.Draw(im)
cx=W//2
# selo
d.rounded_rectangle((cx-150,H//2-195,cx+150,H//2-140),16,fill=VM)
d.text((cx,H//2-167),"EM 3D",font=fo(36),fill=BR,anchor='mm')
t=150
while fo(t).getbbox("PEÇA POR PEÇA",stroke_width=8)[2]>1400: t-=4
d.text((cx,H//2-25),"PEÇA POR PEÇA",font=fo(t),fill=AM,anchor='mm',stroke_width=8,stroke_fill=(0,0,0))
d.text((cx,H//2+95),"Guerra, games e tecnologia explicados, uma peça de cada vez",font=fo(40,b"ExtraBold"),fill=BR,anchor='mm',stroke_width=3,stroke_fill=(0,0,0))
d.text((cx,H//2+160),"NOVOS VÍDEOS TODO DIA  •  SE INSCREVE 🧩".replace(" 🧩",""),font=fo(30,b"Bold"),fill=(200,200,200),anchor='mm')
im.save('banner_canal.png'); im.save('banner_canal.jpg',quality=92)
# prévia com a área segura marcada (só para conferência)
p=im.copy(); pd=ImageDraw.Draw(p)
pd.rectangle(((W-1546)//2,(H-423)//2,(W+1546)//2,(H+423)//2),outline=(0,255,0),width=4)
pd.rectangle(((W-2560)//2,(H-423)//2,(W+2560)//2,(H+423)//2),outline=(0,160,255),width=3)
p.resize((1280,720)).save('previa_area_segura.jpg')

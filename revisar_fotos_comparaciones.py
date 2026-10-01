import json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from comparaciones_por_guia import MODELS
root=Path(__file__).parent
photos=json.loads((root/'fotos-modelos.json').read_text(encoding='utf-8'))['products']
canvas=Image.new('RGB',(1000,260*((len(MODELS)+3)//4)), '#f5f4ef')
draw=ImageDraw.Draw(canvas)
for n,(key,model) in enumerate(MODELS.items()):
    x=(n%4)*250;y=(n//4)*260
    im=Image.open(root/photos[model['source']]['image'].lstrip('/')).convert('RGBA')
    im.thumbnail((224,215))
    canvas.paste(im,(x+(250-im.width)//2,y+(225-im.height)//2),im)
    draw.text((x+10,y+230),key,fill='#141414')
canvas.save(root/'vista-fotos/comparaciones-nuevas.jpg')

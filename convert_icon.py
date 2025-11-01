from PIL import Image
import os

SRC = "Logo Oficial.png"
OUT = "pixapp.ico"

if not os.path.exists(SRC):
    print(f"Arquivo de origem não encontrado: {SRC}")
    raise SystemExit(1)

img = Image.open(SRC).convert('RGBA')
# Create sizes commonly used for .ico
sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
icons = []
for s in sizes:
    icons.append(img.resize(s, Image.LANCZOS))

# save as .ico
icons[0].save(OUT, format='ICO', sizes=sizes)
print(f"Ícone gerado: {OUT}")
